# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Utilities for obtaining speech utterances for objects.  In general,
there probably should be a singleton instance of the SpeechGenerator
class.  For those wishing to override the speech generators, however,
one can create a new instance and replace/extend the speech generators
as they see fit."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import debug
import orca_state
import rolenames
import settings

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import Q_        # to provide qualified translatable strings

class SpeechGenerator:
    """Takes accessible objects and produces a string to speak for
    those objects.  See the getSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speechGenerators instance field as they see fit."""

    def __init__(self, script):

        # The script that created us.  This allows us to ask the
        # script for information if we need it.
        #
        self._script = script

        # Set up a dictionary that maps role names to functions
        # that generate speech for objects that implement that role.
        #
        self.speechGenerators = {}
        self.speechGenerators[pyatspi.ROLE_ALERT]               = \
             self._getSpeechForAlert
        self.speechGenerators[pyatspi.ROLE_ANIMATION]           = \
             self._getSpeechForAnimation
        self.speechGenerators[pyatspi.ROLE_ARROW]               = \
             self._getSpeechForArrow
        self.speechGenerators[pyatspi.ROLE_CHECK_BOX]           = \
             self._getSpeechForCheckBox
        self.speechGenerators[pyatspi.ROLE_CHECK_MENU_ITEM]     = \
             self._getSpeechForCheckMenuItem
        self.speechGenerators[pyatspi.ROLE_COLUMN_HEADER]       = \
             self._getSpeechForColumnHeader
        self.speechGenerators[pyatspi.ROLE_COMBO_BOX]           = \
             self._getSpeechForComboBox
        self.speechGenerators[pyatspi.ROLE_DESKTOP_ICON]        = \
             self._getSpeechForDesktopIcon
        self.speechGenerators[pyatspi.ROLE_DIAL]                = \
             self._getSpeechForDial
        self.speechGenerators[pyatspi.ROLE_DIALOG]              = \
             self._getSpeechForDialog
        self.speechGenerators[pyatspi.ROLE_DIRECTORY_PANE]      = \
             self._getSpeechForDirectoryPane
        self.speechGenerators[pyatspi.ROLE_EMBEDDED]            = \
             self._getSpeechForEmbedded
        self.speechGenerators[pyatspi.ROLE_FRAME]               = \
             self._getSpeechForFrame
        self.speechGenerators[pyatspi.ROLE_HTML_CONTAINER]      = \
             self._getSpeechForHtmlContainer
        self.speechGenerators[pyatspi.ROLE_ICON]                = \
             self._getSpeechForIcon
        self.speechGenerators[pyatspi.ROLE_IMAGE]               = \
             self._getSpeechForImage
        self.speechGenerators[pyatspi.ROLE_LABEL]               = \
             self._getSpeechForLabel
        self.speechGenerators[pyatspi.ROLE_LAYERED_PANE]        = \
             self._getSpeechForLayeredPane
        self.speechGenerators[pyatspi.ROLE_LIST]                = \
             self._getSpeechForList
        self.speechGenerators[pyatspi.ROLE_LIST_ITEM]           = \
             self._getSpeechForListItem
        self.speechGenerators[pyatspi.ROLE_MENU]                = \
             self._getSpeechForMenu
        self.speechGenerators[pyatspi.ROLE_MENU_BAR]            = \
             self._getSpeechForMenuBar
        self.speechGenerators[pyatspi.ROLE_MENU_ITEM]           = \
             self._getSpeechForMenuItem
        self.speechGenerators[pyatspi.ROLE_OPTION_PANE]         = \
             self._getSpeechForOptionPane
        self.speechGenerators[pyatspi.ROLE_PAGE_TAB]            = \
             self._getSpeechForPageTab
        self.speechGenerators[pyatspi.ROLE_PAGE_TAB_LIST]       = \
             self._getSpeechForPageTabList
        self.speechGenerators[pyatspi.ROLE_PARAGRAPH]           = \
             self._getSpeechForText
        self.speechGenerators[pyatspi.ROLE_PASSWORD_TEXT]       = \
             self._getSpeechForText
        self.speechGenerators[pyatspi.ROLE_PROGRESS_BAR]        = \
             self._getSpeechForProgressBar
        self.speechGenerators[pyatspi.ROLE_PUSH_BUTTON]         = \
             self._getSpeechForPushButton
        self.speechGenerators[pyatspi.ROLE_RADIO_BUTTON]        = \
             self._getSpeechForRadioButton
        self.speechGenerators[pyatspi.ROLE_RADIO_MENU_ITEM]     = \
             self._getSpeechForRadioMenuItem
        self.speechGenerators[pyatspi.ROLE_ROW_HEADER]          = \
             self._getSpeechForRowHeader
        self.speechGenerators[pyatspi.ROLE_SCROLL_BAR]          = \
             self._getSpeechForScrollBar
        self.speechGenerators[pyatspi.ROLE_SLIDER]              = \
             self._getSpeechForSlider
        self.speechGenerators[pyatspi.ROLE_SPIN_BUTTON]         = \
             self._getSpeechForSpinButton
        self.speechGenerators[pyatspi.ROLE_SPLIT_PANE]          = \
             self._getSpeechForSplitPane
        self.speechGenerators[pyatspi.ROLE_TABLE]               = \
             self._getSpeechForTable
        self.speechGenerators[pyatspi.ROLE_TABLE_CELL]          = \
             self._getSpeechForTableCellRow
        self.speechGenerators[pyatspi.ROLE_TABLE_COLUMN_HEADER] = \
             self._getSpeechForTableColumnHeader
        self.speechGenerators[pyatspi.ROLE_TABLE_ROW_HEADER]    = \
             self._getSpeechForTableRowHeader
        self.speechGenerators[pyatspi.ROLE_TEAROFF_MENU_ITEM]  = \
             self._getSpeechForMenu
        self.speechGenerators[pyatspi.ROLE_TERMINAL]            = \
             self._getSpeechForTerminal
        self.speechGenerators[pyatspi.ROLE_TEXT]                = \
             self._getSpeechForText
        self.speechGenerators[pyatspi.ROLE_TOGGLE_BUTTON]       = \
             self._getSpeechForToggleButton
        self.speechGenerators[pyatspi.ROLE_TOOL_BAR]            = \
             self._getSpeechForToolBar
        self.speechGenerators[pyatspi.ROLE_TREE]                = \
             self._getSpeechForTable
        self.speechGenerators[pyatspi.ROLE_TREE_TABLE]          = \
             self._getSpeechForTable
        self.speechGenerators[pyatspi.ROLE_WINDOW]              = \
             self._getSpeechForWindow

    def _getSpeechForObjectAccelerator(self, obj):
        """Returns a list of utterances that describes the keyboard
        accelerator (and possibly shortcut) for the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """

        utterances = []

        result = self._script.getKeyBinding(obj)
        accelerator = result[2]

        if len(accelerator) > 0:
            utterances.append(accelerator)

        return utterances

    def _getSpeechForObjectAvailability(self, obj):
        """Returns a list of utterances that describes the availability
        of the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """
        state = obj.getState()
        if not state.contains(pyatspi.STATE_SENSITIVE):
            # Translators: this represents an item on the screen that has
            # been set insensitive (or grayed out).
            #
            return [_("grayed")]
        else:
            return []

    def _getSpeechForObjectLabel(self, obj):
        label = self._script.getDisplayedLabel(obj)
        if label:
            return [label]
        else:
            return []

    def _getSpeechForObjectName(self, obj):
        name = self._script.getDisplayedText(obj)
        if name:
            return [name]
        elif obj.description:
            return [obj.description]
        else:
            return []

    def getSpeechForObjectRole(self, obj, role=None):
        if (obj.getRole() != pyatspi.ROLE_UNKNOWN):
            return [rolenames.getSpeechForRoleName(obj, role)]
        else:
            return []

    def _getSpeechForAllTextSelection(self, obj):
        """Check if this object has text associated with it and it's 
        completely selected.

        Arguments:
        - obj: the object being presented
        """

        utterance = []
        try:
            textObj = obj.queryText()
        except:
            pass
        else:
            noOfSelections = textObj.getNSelections()
            if noOfSelections == 1:
                [string, startOffset, endOffset] = \
                   textObj.getTextAtOffset(0, pyatspi.TEXT_BOUNDARY_LINE_START)
                if startOffset == 0 and endOffset == len(string):
                    # Translators: when the user selects (highlights) text in
                    # a document, Orca lets them know this.
                    #
                    # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
                    #
                    utterance = [Q_("text|selected")]

        return utterance

    def _getSpeechForRequiredObject(self, obj):
        """Returns the list of utterances that describe the required state
        of the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """

        if not settings.presentRequiredState:
            return []

        state = obj.getState()
        if state.contains(pyatspi.STATE_REQUIRED):
            return [settings.speechRequiredStateString]
        else:
            return []

    def _debugGenerator(self, generatorName, obj, already_focused, utterances):
        """Prints debug.LEVEL_FINER information regarding the speech generator.

        Arguments:
        - generatorName: the name of the generator
        - obj: the object being presented
        - already_focused: False if object just received focus
        - utterances: the generated text
        """

        debug.println(debug.LEVEL_FINER,
                      "GENERATOR: %s" % generatorName)
        debug.println(debug.LEVEL_FINER,
                      "           obj             = %s" % obj.name)
        debug.println(debug.LEVEL_FINER,
                      "           role            = %s" % obj.getRoleName())
        debug.println(debug.LEVEL_FINER,
                      "           already_focused = %s" % already_focused)
        debug.println(debug.LEVEL_FINER,
                      "           utterances:")
        for text in utterances:
            debug.println(debug.LEVEL_FINER,
                      "               (%s)" % text)

    def _getDefaultSpeech(self, obj, already_focused, role=None):
        """Gets a list of utterances to be spoken for the current
        object's name, role, and any accelerators.  This is usually the
        fallback speech generator should no other specialized speech
        generator exist for this object.

        The default speech will be of the following form:

        label name role availability

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus
        - role: A role that should be used instead of the Accessible's 
          possible role.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self._getSpeechForAllTextSelection(obj))
            utterances.extend(self.getSpeechForObjectRole(obj, role))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getDefaultSpeech",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForAlert(self, obj, already_focused):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.

        Arguments:
        - obj: the Accessible dialog
        - already_focused: False if object just received focus

        Returns a list of utterances be spoken.
        """

        utterances = []
        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        # Find all the unrelated labels in the dialog and speak them.
        #
        labels = self._script.findUnrelatedLabels(obj)
        for label in labels:
            name = self._getSpeechForObjectName(label)
            utterances.extend(name)

        self._debugGenerator("_getSpeechForAlert",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForAnimation(self, obj, already_focused):
        """Gets the speech for an animation.

        Arguments:
        - obj: the animation
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken.
        """

        utterances = []
        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        self._debugGenerator("_getSpeechForAnimation",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForArrow(self, obj, already_focused):
        """Gets a list of utterances to be spoken for an arrow.

        Arguments:
        - obj: the arrow
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: determine orientation of arrow.  Logged as bugzilla bug
        # 319744.]]]
        # text = arrow direction (left, right, up, down)
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForArrow",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForCheckBox(self, obj, already_focused):
        """Get the speech for a check box.  If the check box already had
        focus, then only the state is spoken.

        Arguments:
        - obj: the check box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("partially checked")
        elif state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("checked")
        else:
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("not checked")

        # If it's not already focused, say it's name
        #
        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            if obj.getRole() == pyatspi.ROLE_TABLE_CELL:
                utterances.extend(
                  self.getSpeechForObjectRole(
                    obj, pyatspi.ROLE_CHECK_BOX))
            else:
                utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(checkedState)
            utterances.extend(self._getSpeechForObjectAvailability(obj))
            utterances.extend(self._getSpeechForRequiredObject(obj))
        else:
            utterances.append(checkedState)

        self._debugGenerator("_getSpeechForCheckBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForCheckMenuItem(self, obj, already_focused):
        """Get the speech for a check menu item.  If the check menu item
        already had focus, then only the state is spoken.

        Arguments:
        - obj: the check menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForCheckBox(obj, already_focused)

        if (settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE)\
           and not already_focused:
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        self._debugGenerator("_getSpeechForCheckMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForColumnHeader(self, obj, already_focused):
        """Get the speech for a column header.

        Arguments:
        - obj: the column header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForColumnHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForComboBox(self, obj, already_focused):
        """Get the speech for a combo box.  If the combo box already has focus,
        then only the selection is spoken.

        Arguments:
        - obj: the combo box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
        else:
            label = None

        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        if not already_focused:
            utterances.extend(self.getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        for child in obj:
            if child.getRole() == pyatspi.ROLE_TEXT:
                utterances.extend(self._getSpeechForAllTextSelection(child))

        self._debugGenerator("_getSpeechForComboBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDesktopIcon(self, obj, already_focused):
        """Get the speech for a desktop icon.

        Arguments:
        - obj: the desktop icon
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDesktopIcon",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDial(self, obj, already_focused):
        """Get the speech for a dial.

        Arguments:
        - obj: the dial
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - might need to include the value here?  Logged as
        # bugzilla bug 319746.]]]
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDial",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDialog(self, obj, already_focused):
        """Get the speech for a dialog box.

        Arguments:
        - obj: the dialog box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForAlert(obj, already_focused)

        self._debugGenerator("_getSpeechForDialog",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDirectoryPane(self, obj, already_focused):
        """Get the speech for a directory pane.

        Arguments:
        - obj: the dial
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDirectoryPane",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForEmbedded(self, obj, already_focused, role=None):
        """Gets a list of utterances to be spoken for the current
        embedded component (i.e., something in a panel).

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus
        - role: A role that should be used instead of the Accessible's 
          possible role.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)
        if not utterances:
            try:
                utterances.append(obj.getApplication().name)
            except:
                pass

        self._debugGenerator("_getSpeechForEmbedded",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForFrame(self, obj, already_focused):
        """Get the speech for a frame.

        Arguments:
        - obj: the frame
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self._getSpeechForAllTextSelection(obj))
            utterances.extend(self.getSpeechForObjectRole(obj))

            # If this application has more than one unfocused alert or
            # dialog window, then speak '<m> unfocused dialogs'
            # to let the user know.
            #
            alertAndDialogCount = \
                        self._script.getUnfocusedAlertAndDialogCount(obj)
            if alertAndDialogCount > 0:
                # Translators: this tells the user how many unfocused
                # alert and dialog windows that this application has.
                #
                line = ngettext("%d unfocused dialog",
                                "%d unfocused dialogs",
                                alertAndDialogCount) % alertAndDialogCount
                utterances.append(line)

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getSpeechForFrame",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForHtmlContainer(self, obj, already_focused):
        """Get the speech for an HTML container.

        Arguments:
        - obj: the dial
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForHtmlContainer",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForIcon(self, obj, already_focused):
        """Get the speech for an icon.

        Arguments:
        - obj: the icon
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - HACK to remove availability output because nautilus
        # doesn't include this information for desktop icons.  If, at some
        # point, it is determined that availability should be added back in,
        # then a custom script for nautilus needs to be written to remove the
        # availability.]]]
        #
        utterances = []
        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)
        
        try:
            image = obj.queryImage()
        except NotImplementedError:
            pass
        else:
            description = image.imageDescription
            if description and len(description):
                utterances.append(description)

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.append(
              rolenames.getSpeechForRoleName(
                obj, pyatspi.ROLE_ICON))

        self._debugGenerator("_getSpeechForIcon",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForImage(self, obj, already_focused):
        """Get the speech for an image.

        Arguments:
        - obj: the image
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(
            obj, already_focused, pyatspi.ROLE_IMAGE)

        self._debugGenerator("_getSpeechForImage",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForLabel(self, obj, already_focused):
        """Get the speech for a label.

        Arguments:
        - obj: the label
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForLabel",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForLayeredPane(self, obj, already_focused):
        """Get the speech for a layered pane

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForLayeredPane",
                             obj,
                             already_focused,
                             utterances)

        # If this has no children, then let the user know.
        #
        hasItems = False
        for child in obj:
            state = child.getState()
            if state.contains(pyatspi.STATE_SHOWING):
                hasItems = True
                break
        if not hasItems:
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            utterances.append(_("0 items"))

        return utterances

    def _getSpeechForList(self, obj, already_focused):
        """Get the speech for a list.

        Arguments:
        - obj: the list
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - include how many items in the list?
        # Logged as bugzilla bug 319749.]]]
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForList",
                             obj,
                             already_focused,
                             utterances)

        return utterances
    
    def _getSpeechForListItem(self, obj, already_focused):
        """Get the speech for a listitem.

        Arguments:
        - obj: the listitem
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
 
        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self._getSpeechForAllTextSelection(obj))
        utterances.extend(self._getSpeechForObjectAvailability(obj))

        # If already in focus then the tree probably collapsed or expanded
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("expanded"))
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("collapsed"))
                
        self._debugGenerator("_getSpeechForListItem",
                             obj,
                             already_focused,
                             utterances)
        return utterances

    def _getSpeechForMenu(self, obj, already_focused):
        """Get the speech for a menu.

        Arguments:
        - obj: the menu
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        if (obj == orca_state.locusOfFocus) \
               and (settings.speechVerbosityLevel \
                    == settings.VERBOSITY_LEVEL_VERBOSE):
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        self._debugGenerator("_getSpeechForMenu",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForMenuBar(self, obj, already_focused):
        """Get the speech for a menu bar.

        Arguments:
        - obj: the menu bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForMenuBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForMenuItem(self, obj, already_focused):
        """Get the speech for a menu item.

        Arguments:
        - obj: the menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # No need to say "menu item" because we already know that.
        #
        utterances = self._getSpeechForObjectName(obj)
        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.extend(self._getSpeechForObjectAvailability(obj))
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        # OpenOffice check menu items currently have a role of "menu item"
        # rather then "check menu item", so we need to test if one of the
        # states is CHECKED. If it is, then add that in to the list of
        # speech utterances. Note that we can't tell if this is a "check
        # menu item" that is currently unchecked and speak that state. 
        # See Orca bug #433398 for more details.
        #
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checked menu item.
            #
            utterances.append(_("checked"))

        self._debugGenerator("_getSpeechForMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForText(self, obj, already_focused):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - HACK to remove availability because some text
        # areas, such as those in yelp, come up as insensitive though
        # they really are ineditable.]]]
        #
        utterances = []
        utterances.extend(self._getSpeechForObjectLabel(obj))
        if len(utterances) == 0:
            if obj.name and (len(obj.name)):
                utterances.append(obj.name)

        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            utterances.append(settings.speechReadOnlyString)

        if obj.getRole() != pyatspi.ROLE_PARAGRAPH:
            utterances.extend(self.getSpeechForObjectRole(obj))

        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        utterances.append(text)

        utterances.extend(self._getSpeechForAllTextSelection(obj))

        self._debugGenerator("_getSpeechForText",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForOptionPane(self, obj, already_focused):
        """Get the speech for an option pane.

        Arguments:
        - obj: the option pane
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForOptionPane",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForPageTab(self, obj, already_focused):
        """Get the speech for a page tab.

        Arguments:
        - obj: the page tab
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForPageTab",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForPageTabList(self, obj, already_focused):
        """Get the speech for a page tab list.

        Arguments:
        - obj: the page tab list
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        #if obj.childCount == 1:
        #    utterances.append(_("one tab"))
        #else:
        #    utterances.append(("%d " % obj.childCount) + _("tabs"))

        self._debugGenerator("_getSpeechForPageTabList",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForProgressBar(self, obj, already_focused):
        """Get the speech for a progress bar.  If the object already
        had focus, just the new value is spoken.

        Arguments:
        - obj: the progress bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        value = obj.queryValue()
        percentValue = (value.currentValue / \
            (value.maximumValue - value.minimumValue)) * 100.0

        # Translators: this is the percentage value of a progress bar.
        #
        percentage = _("%d percent.") % percentValue + " "

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self.getSpeechForObjectRole(obj))

        utterances.append(percentage)

        self._debugGenerator("_getSpeechForProgressBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForPushButton(self, obj, already_focused):
        """Get the speech for a push button

        Arguments:
        - obj: the push button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForPushButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForRadioButton(self, obj, already_focused):
        """Get the speech for a radio button.  If the button already had
        focus, then only the state is spoken.

        Arguments:
        - obj: the check box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
            #
            selectionState = Q_("radiobutton|selected")
        else:
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
            #
            selectionState = Q_("radiobutton|not selected")

        # If it's not already focused, say it's name
        #
        if not already_focused:
            # The label is handled as a context in default.py
            #
            #utterances.extend(self._getSpeechForObjectLabel(obj))
            utterances.extend(self._getSpeechForObjectName(obj))
            utterances.append(selectionState)
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(selectionState)

        self._debugGenerator("_getSpeechForRadioButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForRadioMenuItem(self, obj, already_focused):
        """Get the speech for a radio menu item.  If the menu item
        already had focus, then only the state is spoken.

        Arguments:
        - obj: the check menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForRadioButton(obj, False)

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.extend(self._getSpeechForObjectAvailability(obj))
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        self._debugGenerator("_getSpeechForRadioMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForRowHeader(self, obj, already_focused):
        """Get the speech for a row header.

        Arguments:
        - obj: the column header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForRowHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForScrollBar(self, obj, already_focused):
        """Get the speech for a scroll bar.

        Arguments:
        - obj: the scroll bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - want to get orientation and maybe the
        # percentage scrolled so far. Logged as bugzilla bug
        # 319744.]]]
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForScrollBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForSlider(self, obj, already_focused):
        """Get the speech for a slider.  If the object already
        had focus, just the value is spoken.

        Arguments:
        - obj: the slider
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        valueString = self._script.getTextForValue(obj)

        if already_focused:
            utterances = [valueString]
        else:
            utterances = []
            utterances.extend(self._getSpeechForObjectLabel(obj))
            # Ignore the text on the slider.  See bug 340559
            # (http://bugzilla.gnome.org/show_bug.cgi?id=340559): the
            # implementors of the slider support decided to put in a
            # Unicode left-to-right character as part of the text,
            # even though that is not painted on the screen.
            #
            # In Java, however, there are sliders without a label. In
            # this case, we'll add to presentation the slider name if
            # it exists and we haven't found anything yet.
            #
            if not utterances:
                utterances.extend(self._getSpeechForObjectName(obj))
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(valueString)
            utterances.extend(self._getSpeechForObjectAvailability(obj))
            utterances.extend(self._getSpeechForRequiredObject(obj))

        self._debugGenerator("_getSpeechForSlider",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForSpinButton(self, obj, already_focused):
        """Get the speech for a spin button.  If the object already has
        focus, then only the new value is spoken.

        Arguments:
        - obj: the spin button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        if already_focused:
            utterances = [self._script.getDisplayedText(obj)]
        else:
            utterances = self._getDefaultSpeech(obj, already_focused)
            utterances.extend(self._getSpeechForRequiredObject(obj))

        self._debugGenerator("_getSpeechForSpinButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForSplitPane(self, obj, already_focused):
        """Get the speech for a split pane.

        Arguments:
        - obj: the split pane
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        valueString = self._script.getTextForValue(obj)

        if already_focused:
            utterances = [valueString]
        else:
            utterances = []
            utterances.extend(self._getSpeechForObjectLabel(obj))
            if not utterances:
                utterances.extend(self._getSpeechForObjectName(obj))
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(valueString)
            utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getSpeechForSplitPane",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTable(self, obj, already_focused):
        """Get the speech for a table

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTable",
                             obj,
                             already_focused,
                             utterances)

        # If this is a table with no children, then let the user know.
        #
        if not obj.childCount:
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            utterances.append(_("0 items"))

        return utterances

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech utterances for a single table cell

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        # If this table cell has 2 children and one of them has a 
        # 'toggle' action and the other does not, then present this 
        # as a checkbox where:
        # 1) we get the checked state from the cell with the 'toggle' action
        # 2) we get the label from the other cell.
        # See Orca bug #376015 for more details.
        #
        if obj.childCount == 2:
            cellOrder = []
            hasToggle = [ False, False ]
            for i, child in enumerate(obj):
                try:
                    action = child.queryAction()
                except NotImplementedError:
                    continue
                else:
                    for j in range(0, action.nActions):
                        # Translators: this is the action name for
                        # the 'toggle' action. It must be the same
                        # string used in the *.po file for gail.
                        #
                        if action.getName(j) in ["toggle", _("toggle")]:
                            hasToggle[i] = True
                            break

            if hasToggle[0] and not hasToggle[1]:
                cellOrder = [ 1, 0 ] 
            elif not hasToggle[0] and hasToggle[1]:
                cellOrder = [ 0, 1 ]
            if cellOrder:
                for i in cellOrder:
                    # Don't speak the label if just the checkbox state has
                    # changed.
                    #
                    if already_focused and not hasToggle[i]:
                        pass
                    else:
                        utterances.extend( \
                            self._getSpeechForTableCell(obj[i],
                                                        already_focused))
                return utterances

        # [[[TODO: WDW - Attempt to infer the cell type.  There's a
        # bunch of stuff we can do here, such as check the EXPANDABLE
        # state, check the NODE_CHILD_OF relation, etc.  Logged as
        # bugzilla bug 319750.]]]
        #
        try:
            action = obj.queryAction()
        except NotImplementedError:
            action = None
        if action:
            for i in range(0, action.nActions):
                debug.println(debug.LEVEL_FINEST,
                    "speechgenerator.__getTableCellUtterances " \
                    + "looking at action %d" % i)

                # Translators: this is the action name for
                # the 'toggle' action. It must be the same
                # string used in the *.po file for gail.
                #
                if action.getName(i) in ["toggle", _("toggle")]:
                    utterances = self._getSpeechForCheckBox(obj,
                                                            already_focused)
                    break

        displayedText = self._script.getDisplayedText( \
                          self._script.getRealActiveDescendant(obj))
        if not already_focused and not displayedText in utterances:
            utterances.append(displayedText)

        # If there is no displayed text, check to see if this table cell 
        # contains an icon (image). If yes:
        #   1/ Try to get a description for it and speak that.
        #   2/ Treat the object of role type ROLE_IMAGE and speak
        #      the role name.
        # See bug #465989 for more details.
        #
        # [[TODO: eitani - incorprate this in new rolenames ]]
        try:
            image = obj.queryImage()
        except:
            image = None

        if (not displayedText or len(displayedText) == 0) and image:
            if not already_focused:
                if image.imageDescription:
                    utterances.append(image.imageDescription)
                utterances.extend(self._getSpeechForImage(obj, already_focused))

        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("expanded"))
                childNodes = self._script.getChildNodes(obj)
                children = len(childNodes)

                if not children \
                   or (settings.speechVerbosityLevel == \
                       settings.VERBOSITY_LEVEL_VERBOSE):
                    # Translators: this is the number of items in a layered
                    # pane or table.
                    #
                    itemString = ngettext("%d item",
                                          "%d items",
                                          children) % children
                    utterances.append(itemString)
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("collapsed"))

        utterances.extend(self._getSpeechForRequiredObject(obj))

        self._debugGenerator("_getSpeechForTableCell",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTableCellRow(self, obj, already_focused):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False.

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if (not already_focused):
            try:
                parent_table = obj.parent.queryTable()
            except NotImplementedError:
                parent_table = None
            if settings.readTableCellRow and parent_table \
                and (not self._script.isLayoutOnly(obj.parent)):
                parent = obj.parent
                index = self._script.getCellIndex(obj)
                row = parent_table.getRowAtIndex(index)
                column = parent_table.getColumnAtIndex(index)

                # This is an indication of whether we should speak all the
                # table cells (the user has moved focus up or down a row),
                # or just the current one (focus has moved left or right in
                # the same row).
                #
                speakAll = True
                if "lastRow" in self._script.pointOfReference and \
                    "lastColumn" in self._script.pointOfReference:
                    pointOfReference = self._script.pointOfReference
                    speakAll = (pointOfReference["lastRow"] != row) or \
                        ((row == 0 or row == parent_table.nRows-1) and \
                           pointOfReference["lastColumn"] == column)

                if speakAll:
                    for i in range(0, parent_table.nColumns):
                        cell = parent_table.getAccessibleAt(row, i)
                        if not cell:
                            debug.println(debug.LEVEL_WARNING,
                                 "ERROR: speechgenerator." \
                                 + "_getSpeechForTableCellRow" \
                                 + " no accessible at (%d, %d)" % (row, i))
                            continue
                        state = cell.getState()
                        showing = state.contains(pyatspi.STATE_SHOWING)
                        if showing:
                            # If this table cell has a "toggle" action, and
                            # doesn't have any label associated with it then 
                            # also speak the table column header.
                            # See Orca bug #455230 for more details.
                            #
                            label = self._script.getDisplayedText( \
                                self._script.getRealActiveDescendant(cell))
                            try:
                                action = cell.queryAction()
                            except NotImplementedError:
                                action = None
                            if action and (label == None or len(label) == 0):
                                for j in range(0, action.nActions):
                                    # Translators: this is the action name for
                                    # the 'toggle' action. It must be the same
                                    # string used in the *.po file for gail.
                                    #
                                    if action.getName(j) in ["toggle", \
                                                             _("toggle")]:
                                        accHeader = \
                                            parent_table.getColumnHeader(i)
                                        utterances.append(accHeader.name)

                            utterances.extend(self._getSpeechForTableCell(cell,
                                                           already_focused))
                else:
                    utterances.extend(self._getSpeechForTableCell(obj,
                                                           already_focused))
            else:
                utterances = self._getSpeechForTableCell(obj, already_focused)
        else:
            utterances = self._getSpeechForTableCell(obj, already_focused)

        self._debugGenerator("_getSpeechForTableCellRow",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTableColumnHeader(self, obj, already_focused):
        """Get the speech for a table column header

        Arguments:
        - obj: the table column header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForColumnHeader(obj, already_focused)

        self._debugGenerator("_getSpeechForTableColumnHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTableRowHeader(self, obj, already_focused):
        """Get the speech for a table row header

        Arguments:
        - obj: the table row header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForRowHeader(obj, already_focused)

        self._debugGenerator("_getSpeechForTableRowHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTearOffMenuItem(self, obj, already_focused):
        """Get the speech for a tear off menu item

        Arguments:
        - obj: the tear off menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances = [rolenames.getSpeechForRoleName(obj)]
        else:
            # Translators: brief spoken words for the rolename of a tear off
            # menu item.
            #
            utterances = [_("tear off")]

        self._debugGenerator("_getSpeechForTearOffMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTerminal(self, obj, already_focused):
        """Get the speech for a terminal

        Arguments:
        - obj: the terminal
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        title = None
        frame = self._script.getFrame(obj)
        if frame:
            title = frame.name
        if not title:
            title = self._script.getDisplayedLabel(obj)

        utterances = [title]

        self._debugGenerator("_getSpeechForTerminal",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForToggleButton(self, obj, already_focused):
        """Get the speech for a toggle button.  If the toggle button already
        had focus, then only the state is spoken.

        Arguments:
        - obj: the check box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: the state of a toggle button.
            #
            checkedState = _("pressed")
        else:
            # Translators: the state of a toggle button.
            #
            checkedState = _("not pressed")

        # If it's not already focused, say it's name
        #
        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(checkedState)
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(checkedState)

        self._debugGenerator("_getSpeechForToggleButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForToolBar(self, obj, already_focused):
        """Get the speech for a tool bar

        Arguments:
        - obj: the tool bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForToolBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTree(self, obj, already_focused):
        """Get the speech for a tree

        Arguments:
        - obj: the tree
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTree",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTreeTable(self, obj, already_focused):
        """Get the speech for a tree table

        Arguments:
        - obj: the tree table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTreeTable",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForWindow(self, obj, already_focused):
        """Get the speech for a window

        Arguments:
        - obj: the window
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForWindow",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def getSpeech(self, obj, already_focused):
        """Get the speech for an Accessible object.  This will look
        first to the specific speech generators and then to the
        default speech generator.  This method is the primary method
        that external callers of this class should use.

        Arguments:
        - obj: the object
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken.
        """
        role = obj.getRole()
        if role in self.speechGenerators:
            generator = self.speechGenerators[role]
        else:
            generator = self._getDefaultSpeech

        return [" ".join(generator(obj, already_focused))]

    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

        Arguments:
        - obj: the object
        - stopAncestor: the anscestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if not obj:
            return utterances

        if obj == stopAncestor:
            return utterances

        parent = obj.parent
        if parent \
            and (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
            and (parent.getRole() == pyatspi.ROLE_TABLE_CELL):
            parent = parent.parent

        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break
            if not self._script.isLayoutOnly(parent):
                text = self._script.getDisplayedLabel(parent)
                if not text and 'Text' in pyatspi.listInterfaces(parent):
                    text = self._script.getDisplayedText(parent)
                if text and len(text.strip()):
                    # Push announcement of cell to the end
                    #
                    if parent.getRole() not in [pyatspi.ROLE_TABLE_CELL,
                                                pyatspi.ROLE_FILLER]:
                        utterances.append(\
                            rolenames.getSpeechForRoleName(parent))
                    utterances.append(text)
                    if parent.getRole() == pyatspi.ROLE_TABLE_CELL:
                        utterances.append(\
                            rolenames.getSpeechForRoleName(parent))
            parent = parent.parent

        utterances.reverse()

        return utterances
