# Orca
#
# Copyright 2006-2007 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import atspi
import default
import debug
import orca
import orca_state
import keybindings
import settings
import speech
import rolenames
import Accessibility
import speechgenerator

from orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# The Java script class.                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForLabel
    """
    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForLabel(self, obj, already_focused):
        """Get the speech for a label.

        Arguments:
        - obj: the label
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances=[]
        if (not already_focused):
            utterances = self._getDefaultSpeech(obj, already_focused)

        obj.was_selected = False
        if obj.state.count(Accessibility.STATE_EXPANDED) != 0:
            # Translators: this represents the state of a node in a tree.
            # 'expanded' means the children are showing.
            # 'collapsed' means the children are not showing.
            #
            utterances.append(_("expanded"))
        elif obj.state.count(Accessibility.STATE_EXPANDED) == 0 and \
                obj.state.count(Accessibility.STATE_EXPANDABLE) != 0:
            # Translators: this represents the state of a node in a tree.
            # 'expanded' means the children are showing.
            # 'collapsed' means the children are not showing.
            #
            utterances.append(_("collapsed"))
        elif obj.state.count(Accessibility.STATE_SELECTED) != 0:
            utterances.append(_("selected"))
            obj.was_selected = True
        elif obj.state.count(Accessibility.STATE_SELECTED) == 0 and \
                obj.state.count(Accessibility.STATE_SELECTABLE) != 0:
            utterances.append(_("unselected"))

        self._debugGenerator("_getSpeechForLabel",
                             obj,
                             already_focused,
                             utterances)

        return utterances

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for Java applications.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        default.Script.__init__(self, app)

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "J2SE-access-bridge.py: "+msg)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """
        keysym = keyboardEvent.event_string
        keyboardEvent.hw_code = keybindings.getKeycode(keysym)
        return default.Script.consumesKeyboardEvent(self, keyboardEvent)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        self._debug("onFocus: %s '%s'" % \
                    (event.source.role, event.source.name))

        role = event.source.role
        if role == rolenames.ROLE_LIST:
            selectedItem = None
            selection = event.source.selection
            if selection and selection.nSelectedChildren > 0:
                selectedItem = atspi.Accessible.makeAccessible(
                                        selection.getSelectedChild(0))
            elif event.source.childCount > 0:
                selectedItem = event.source.child(0)
            if selectedItem:
                orca.setLocusOfFocus(event, selectedItem)
            else:
                # if impossible to get selection or list has 0 items, present list
                orca.setLocusOfFocus(event, event.source)
        elif role == rolenames.ROLE_LABEL:
            # In FileChooserDemo, when enter in a new folder, a focus event for
            # the top combo box selected item (not SHOWING item) is received.
            # Should this check be more specific ?
            #
            if not event.source.state.count (Accessibility.STATE_SHOWING):
                return
        elif role == rolenames.ROLE_MENU:
            # A JMenu has always selection.nSelectedChildren > 0
            orca.setLocusOfFocus(event, event.source)
        else:
            default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.  Currently, the
        state changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        self._debug("onStateChanged: %s: %s '%s' (%d,%d)" % \
                    (event.type, event.source.role, event.source.name, event.detail1, event.detail2))

        # This is a workaround for a java-access-bridge bug (Bug 355011)
        # where popup menu events are not sent to Orca.
        #
        # When a root pane gets focus, a popup menu may have been invoked.
        # If there is a popup menu, give locus of focus to the armed menu
        # item.
        #
        if event.source.role == rolenames.ROLE_ROOT_PANE and \
               event.type == "object:state-changed:focused" and \
               event.detail1 == 1:

            for i in range(0, event.source.childCount):
                # search the layered pane for a popup menu
                child = event.source.child(i)
                if child.role == rolenames.ROLE_LAYERED_PANE:
                    popup = self.findByRole(child, rolenames.ROLE_POPUP_MENU, False)
                    if len(popup) > 0:
                        # set the locus of focus to the armed menu item
                        items = self.findByRole(popup[0], rolenames.ROLE_MENU_ITEM, False)
                        for item in items:
                            if item.state.count(Accessibility.STATE_ARMED):
                                orca.setLocusOfFocus(event, item)
                                return


        # In java applications the events are comming in other order:
        # "focus:" event comes before "state-changed:focused" event
        #
        if (event.type == "object:state-changed:focused"):
            return

        # Hand state changes when JTree labels become expanded
        # or collapsed.
        #
        if ((event.source.role == rolenames.ROLE_LABEL) and \
            (event.type == "object:state-changed:expanded")):
            orca.visualAppearanceChanged(event, event.source)
            return

        # Present a value change in case of an focused popup menu.
        # Fix for Swing file chooser.
        #
        if event.type == "object:state-changed:visible" and \
                event.source.role == rolenames.ROLE_POPUP_MENU and \
                event.source.parent.state.count(Accessibility.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source.parent)
            return

        default.Script.onStateChanged(self, event)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        self._debug("onSelectionChanged: %s '%s'" % \
                    (event.source.role, event.source.name))

        if not event.source.state.count (atspi.Accessibility.STATE_FOCUSED):
            return

        if event.source.role == rolenames.ROLE_TABLE:
            return

        if event.source.role == rolenames.ROLE_TREE:
            return

        if event.source.role == rolenames.ROLE_LIST:
            selection = event.source.selection
            if selection.nSelectedChildren <= 0:
                if event.source.childCount > 0:
                    child = event.source.child(0)
                    if child.state.count (atspi.Accessibility.STATE_ACTIVE):
                        return
                else:
                    orca.setLocusOfFocus(event, event.source)
                    return
            else:
                selectedItem = atspi.Accessible.makeAccessible(
                                        selection.getSelectedChild(0))

                # If the selected list item is the same with the last focused object,
                # present it only if the item was not selected and has SELECTED state
                # or if the item doesn't have SELECTED state, but SELECTABLE and
                # it was selected.
                #
                if orca_state.activeScript and \
                   orca_state.activeScript.isSameObject(selectedItem,  \
                                                    orca_state.locusOfFocus):
                    if (orca_state.locusOfFocus.state.count(Accessibility.STATE_SELECTED) != 0 \
                                and not orca_state.locusOfFocus.was_selected)   \
                        or (orca_state.locusOfFocus.state.count(Accessibility.STATE_SELECTED) == 0 \
                                and orca_state.locusOfFocus.state.count(Accessibility.STATE_SELECTABLE) != 0 \
                                and orca_state.locusOfFocus.was_selected):
                        orca.visualAppearanceChanged(event, selectedItem)
                    return

        default.Script.onSelectionChanged(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        self._debug("onValueChanged: %s '%s' value=%d" % \
                    (event.source.role, event.source.name,
                     event.source.value.currentValue))

        # We'll let state-changed:checked event to be used to
        # manage check boxes in java application
        #
        if event.source.role == rolenames.ROLE_CHECK_BOX and \
               event.type == "object:property-change:accessible-value":
            return

        default.Script.onValueChanged(self, event)


    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.  This
        method should not be called for objects whose visual appearance
        changes solely because of focus -- setLocusOfFocus is used for that.
        Instead, it is intended mostly for objects whose notional 'value' has
        changed, such as a checkbox changing state, a progress bar advancing,
        a slider moving, text inserted, caret moved, etc.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        self._debug("visualAppearanceChanged: %s '%s', locusOfFocus=%s" % \
                    (obj.role, obj.name, orca_state.locusOfFocus.role))

        # Present to Braille and Speech an object that is the same
        # with the last focused object, only if it is a label.
        # This case is for LISTs which contain labels as items
        # (see Open dialog lists).
        #
        if orca_state.activeScript.isSameObject(obj, orca_state.locusOfFocus):
            if obj.role == rolenames.ROLE_LABEL:
                self.updateBraille(orca_state.locusOfFocus)
                speech.speakUtterances(self.speechGenerator.getSpeech(orca_state.locusOfFocus, True))
                return

        if obj.role == rolenames.ROLE_SPIN_BOX:
            # Check for the spinbox text object being null. There appears
            # to be a bug where the text object for some text fields
            # is null. 
            if orca_state.locusOfFocus.role == rolenames.ROLE_TEXT and \
               orca_state.locusOfFocus.text == None:
                # Set the locusOfFocus to the spinbox itself.
                orca.setLocusOfFocus(event, obj)

        default.Script.visualAppearanceChanged(self, event, obj)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        self._debug("onCaretMoved: %s '%s'" % \
                    (event.source.role, event.source.name))

        # Check for bogus events containing null text objects.
        if event.source.text == None:
            self._debug("bogus event: text object is null. Discarding event")
            return;

        default.Script.onCaretMoved(self, event)

    def onTextInserted(self, event):
        """Called whenever the text is inserted.

        Arguments:
        - event: the Event
        """

        self._debug("onTextInserted: %s '%s'" % \
                    (event.source.role, event.source.name))

        # Check for bogus events containing null text objects.
        if event.source.text == None:
            self._debug("bogus event: text object is null. Discarding event")
            return;

        default.Script.onTextInserted(self, event)        

    def getDisplayedLabel(self, object):
        """If there is an object labelling the given object, return the
        text being displayed for the object labelling this object.
        Otherwise, return None.

        Argument:
        - object: the object in question

        Returns the string of the object labelling this object, or None
        if there is nothing of interest here.
        """
        label = default.Script.getDisplayedLabel(self, object)
        if not label and \
           (object.role == rolenames.ROLE_TEXT or \
            object.role == rolenames.ROLE_COMBO_BOX):
            # This is a workaround for a common Java accessibility
            # bug where a label next to a component is used to
            # label the component. This relation is only obvious to
            # a sighted person. The LABEL_FOR property is used to
            # indicate the label refers to the component next to it.
            # The workaround is to assume the label refers to the
            # component if the label is the previous component and
            # ends with a colon. We only do this for text and combo
            # boxes since they are the most common Java component with
            # this bug.
            if object.index > 0:
                prevSibling = object.parent.child(object.index-1)
                if prevSibling and prevSibling.name and \
                   prevSibling.role == rolenames.ROLE_LABEL:
                    labelFor = prevSibling.name.rstrip(" ")
                    if (labelFor.endswith(":")):
                        return labelFor.rstrip(":")

        return label
