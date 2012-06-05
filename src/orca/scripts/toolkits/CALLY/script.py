# Orca
#
# Copyright (C) 2010-2012 Igalia, S.L.
#
# Author: Alejandro Pinheiro Iglesias <apinheiro@igalia.com>
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010-2012 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import time
from gi.repository import Gdk

import orca.orca as orca
import orca.scripts.default as default
import orca.debug as debug

# Set with non printable unicode categories. Full table:
# http://www.fileformat.info/info/unicode/category/index.htm
#
non_printable_set = ('Cc', 'Cf', 'Cn', 'Co', 'Cs')

########################################################################
#                                                                      #
# Utility methods.                                                     #
#                                                                      #
########################################################################

def _unicharIsPrint(unichar):
    """ Checks if the unichar is printable

    Equivalent to g_unichar_isprint

    Arguments:
    - unichar: unichar to check if it is printable
    """
    try:
        import unicodedata
        category = unicodedata.category (unichar)
        result = category not in non_printable_set
    except:
        # Normally a exception is because there are a string
        # instead of a single unicode, 'Control_L'
        #
        result = False

    return result

def _computeIsText(string):
    """Decides if the string representation of a keyboard event is
    text or not

    Based on the at-spi equivalent code.

    Arguments:
    - string: a string representation of a keyboardEvent.
    """
    is_text = False

    if (string):
        char = unicode (string, "UTF-8")
        if (char > 0 and  _unicharIsPrint (char)):
            is_text = True
        else:
            is_text = False
    else:
        is_text = False

    return is_text

def _parentDialog(obj):
    """Looks for an object of ROLE_DIALOG in the ancestry of obj.

    Arguments:
    - obj: an accessible object

    Returns the accessible object if found; otherwise None.
    """

    isDialog = lambda x: x and x.getRole() == pyatspi.ROLE_DIALOG

    return pyatspi.utils.findAncestor(obj, isDialog)

########################################################################
#                                                                      #
# The Cally script class.                                              #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for Cally applications.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)
        self._activeDialog = (None, 0) # (Accessible, Timestamp)
        self._activeDialogLabels = {}  # key == hash(obj), value == name

    def checkKeyboardEventData(self, keyboardEvent):
        """Processes the given keyboard event.

        Here is used to:
        * Fill event_string using the key.id
        * Set the is_text properly

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

        # On the AtkKeyEventStruct documentation you can find this
        # description:
        # guint keyval;
        # A guint representing a keysym value corresponding to those
        # used by GDK
        #
        # There are no Clutter way to get a gdk-like keyvalname.
        # Anyway, cally will fill event_string with the final
        # representation of a text char.
        #
        # In the same way, Clutter provides the keyval without the
        # modifiers, and GDK yes. We will try to apply it, at least
        # to compute keyval_name
        #
        # More information:
        # http://library.gnome.org/devel/atk/stable/AtkUtil.html
        # http://bugzilla.o-hand.com/show_bug.cgi?id=2072

        # apply the modifiers to keyboardEvent.id
        #
        keyval = keyboardEvent.id
        try:
            keymap = Gdk.Keymap.get_default()

            if keymap:
                success, entries = keymap.get_entries_for_keyval(keyval)
                group = entries[0].group
                modifiers = Gdk.ModifierType(keyboardEvent.modifiers)
                success, keyval, egroup, level, consumed = \
                    keymap.translate_keyboard_state (keyboardEvent.hw_code,
                                                     modifiers,
                                                     group)
        except:
            debug.println(debug.LEVEL_FINE,
                          "Could not compute keyval with modifiers")

        string = "prev keyval=%d" % keyboardEvent.id
        string = string + " post keyval=%d" % keyval

        debug.println(debug.LEVEL_FINE, string)

        keyboardEvent.id = keyval

        # if cally doesn't provide a event_string we get that using
        # Gdk. I know that it will probably called again computing
        # keyval_name but to simplify code, and not start to add
        # guess-code here I will maintain that in this way
        #
        if (keyboardEvent.event_string == ""):
            debug.println (debug.LEVEL_FINE, "Computing event_string")
            try:
                keyboardEvent.event_string = Gdk.keyval_name(keyboardEvent.id)
            except:
                debug.println(debug.LEVEL_FINE,
                              "Could not obtain keyval_name for id: %d" \
                                  % keyboardEvent.id)

            # at-spi uses event_string to compute is_text, so if it is
            # NULL we should compute again with the proper
            # event_string
            #
            keyboardEvent.is_text = _computeIsText(keyboardEvent.event_string)

        return default.Script.checkKeyboardEventData(self, keyboardEvent)

    def skipObjectEvent(self, event):
        """Gives us, and scripts, the ability to decide an event isn't
        worth taking the time to process under the current circumstances.

        Arguments:
        - event: the Event

        Returns True if we shouldn't bother processing this object event.
        """

        try:
            role = event.source.getRole()
        except:
            pass
        else:
            # We must handle all dialogs ourselves in this script.
            if role == pyatspi.ROLE_DIALOG:
                return False

        return default.Script.skipObjectEvent(self, event)

    def presentDialogLabel(self, event):
        """Examines and, if appropriate, presents a new or changed label
        found in a dialog box. Returns True if we handled the presentation
        here."""

        try:
            role = event.source.getRole()
            name = event.source.name
        except:
            return False

        activeDialog, timestamp = self._activeDialog
        if not activeDialog or role != pyatspi.ROLE_LABEL:
            return False

        obj = hash(event.source)
        if name == self._activeDialogLabels.get(obj):
            return True

        if activeDialog == _parentDialog(event.source):
            self.presentMessage(name)
            self._activeDialogLabels[obj] = name
            return True

        return False

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        if self.presentDialogLabel(event):
            return

        default.Script.onNameChanged(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        try:
            role = event.source.getRole()
            name = event.source.name
            state = event.source.getState()
        except:
            return

        activeDialog, timestamp = self._activeDialog
        eType = event.type
        if eType.startswith("object:state-changed:showing"):
            # When entering overview with many open windows, we get quite
            # a few state-changed:showing events for nameless panels. The
            # act of processing these by the default script causes us to
            # present nothing, and introduces a significant delay before
            # presenting the Top Bar button when Ctrl+Alt+Tab was pressed.
            if role == pyatspi.ROLE_PANEL and not name:
                return

            # We cannot count on events or their order from dialog boxes.
            # Therefore, the only way to reliably present a dialog is by
            # ignoring the events of the dialog itself and keeping track
            # of the current dialog.
            if not event.detail1 and event.source == activeDialog:
                self._activeDialog = (None, 0)
                self._activeDialogLabels = {}
                return

            if activeDialog and role == pyatspi.ROLE_LABEL and event.detail1:
                if self.presentDialogLabel(event):
                    return

        elif eType.startswith("object:state-changed:focused") and event.detail1:
            # The dialog will get presented when its first child gets focus.
            if role == pyatspi.ROLE_DIALOG:
                return

            # This is to present dialog boxes which are, to the user, newly
            # activated. And if something is claiming to be focused that is
            # not in a dialog, that's good to know as well, so update our
            # state regardless.
            if not activeDialog:
                dialog = _parentDialog(event.source)
                self._activeDialog = (dialog, time.time())
                if dialog:
                    orca.setLocusOfFocus(None, dialog)
                    labels = self.utilities.unrelatedLabels(dialog)
                    for label in labels:
                        self._activeDialogLabels[hash(label)] = label.name

        elif eType.startswith("object:state-changed:selected") and event.detail1:
            # Some buttons, like the Wikipedia button, claim to be selected but
            # lack STATE_SELECTED. The other buttons, such as in the Dash and
            # event switcher, seem to have the right state. Since the ones with
            # the wrong state seem to be things we don't want to present anyway
            # we'll stop doing so and hope we are right.
            if state.contains(pyatspi.STATE_SELECTED):
                orca.setLocusOfFocus(event, event.source)
                return

        default.Script.onStateChanged(self, event)

    def getTextLineAtCaret(self, obj, offset=None):
        """Gets the line of text where the caret is."""

        # TODO - JD/API: This is to work around the braille issue reported
        # in bgo 677221. When that is resolved, this workaround can be
        # removed.
        string, caretOffset, startOffset = \
            default.Script.getTextLineAtCaret(self, obj, offset)

        if string:
            return [string, caretOffset, startOffset]

        try:
            text = obj.queryText()
        except:
            pass
        else:
            string = text.getText(0, -1)

        return [string, caretOffset, startOffset]
