# Orca
#
# Copyright (C) 2010 Igalia, S.L.
#
# Author: Alejandro Pinheiro Iglesias <apinheiro@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Igalia, S.L."
__license__   = "LGPL"

import orca.default as default
import orca.debug as debug
import gtk.gdk as gdk


# Set with non printable unicode categories. Full table:
# http://www.fileformat.info/info/unicode/category/index.htm
#

non_printable_set = ('Cc', 'Cf', 'Cn', 'Co', 'Cs')

########################################################################
#                                                                      #
# Utility string methods.                                              #
#                                                                      #
########################################################################

def _unicharIsPrint (unichar):
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

def _computeIsText (string):
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
            keymap = gdk.keymap_get_default()

            if (keymap):
                result = keymap.get_entries_for_keyval (keyval)
                group = result[0][2]

                keyval, egroup, level, consumed = \
                keymap.translate_keyboard_state (keyboardEvent.hw_code,
                                                 keyboardEvent.modifiers,
                                                 group)
        except:
            debug.println(debug.LEVEL_FINE,
                          "Could not compute keyval with modifiers")

        string = "prev keyval=%d" % keyboardEvent.id
        string = string + " post keyval=%d" % keyval

        debug.println(debug.LEVEL_FINE, string)

        keyboardEvent.id = keyval

        # if cally doesn't provide a event_string we get that using
        # gdk. I know that it will probably called again computing
        # keyval_name but to simplify code, and not start to add
        # guess-code here I will maintain that in this way
        #
        if (keyboardEvent.event_string == ""):
            debug.println (debug.LEVEL_FINE, "Computing event_string")
            try:
                keyboardEvent.event_string = gdk.keyval_name (keyboardEvent.id)
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


