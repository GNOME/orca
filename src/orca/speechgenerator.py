# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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

"""Utilities for obtaining speech utterances for objects.  In general,
there probably should be a singleton instance of the SpeechUtil class.
For those wishing to override the speech generators, however, one can
create a new instance and replace/extend the speech generators as
they see fit."""

import math

import a11y
import core
import debug

import orca
import rolenames
import settings

from orca_i18n import _                          # for gettext support
from rolenames import getSpeechForRoleName       # localized role names

class SpeechGenerator:    
    """Takes accessible objects and produces a string to speak for
    those objects.  See the getSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speechGenerators instance field as they see fit."""
    
    def __init__(self):

        # Set up a dictionary that maps role names to functions
        # that generate speech for objects that implement that role.
        #
        self.speechGenerators = {}
        self.speechGenerators[rolenames.ROLE_ALERT]               = \
             self._getSpeechForAlert
        self.speechGenerators[rolenames.ROLE_ANIMATION]           = \
             self._getSpeechForAnimation
        self.speechGenerators[rolenames.ROLE_ARROW]               = \
             self._getSpeechForArrow
        self.speechGenerators[rolenames.ROLE_CHECK_BOX]           = \
             self._getSpeechForCheckBox
        self.speechGenerators[rolenames.ROLE_CHECK_MENU]          = \
             self._getSpeechForCheckMenuItem
        self.speechGenerators[rolenames.ROLE_CHECK_MENU_ITEM]     = \
             self._getSpeechForCheckMenuItem
        self.speechGenerators[rolenames.ROLE_COLUMN_HEADER]       = \
             self._getSpeechForColumnHeader
        self.speechGenerators[rolenames.ROLE_COMBO_BOX]           = \
             self._getSpeechForComboBox
        self.speechGenerators[rolenames.ROLE_DESKTOP_ICON]        = \
             self._getSpeechForDesktopIcon
        self.speechGenerators[rolenames.ROLE_DIAL]                = \
             self._getSpeechForDial
        self.speechGenerators[rolenames.ROLE_DIALOG]              = \
             self._getSpeechForDialog
        self.speechGenerators[rolenames.ROLE_DIRECTORY_PANE]      = \
             self._getSpeechForDirectoryPane
        self.speechGenerators[rolenames.ROLE_FRAME]               = \
             self._getSpeechForFrame
        self.speechGenerators[rolenames.ROLE_HTML_CONTAINER]      = \
             self._getSpeechForHtmlContainer
        self.speechGenerators[rolenames.ROLE_ICON]                = \
             self._getSpeechForIcon
        self.speechGenerators[rolenames.ROLE_IMAGE]               = \
             self._getSpeechForImage
        self.speechGenerators[rolenames.ROLE_LABEL]               = \
             self._getSpeechForLabel
        self.speechGenerators[rolenames.ROLE_LIST]                = \
             self._getSpeechForList
        self.speechGenerators[rolenames.ROLE_MENU]                = \
             self._getSpeechForMenu
        self.speechGenerators[rolenames.ROLE_MENU_BAR]            = \
             self._getSpeechForMenuBar
        self.speechGenerators[rolenames.ROLE_MENU_ITEM]           = \
             self._getSpeechForMenuItem
        self.speechGenerators[rolenames.ROLE_OPTION_PANE]         = \
             self._getSpeechForOptionPane
        self.speechGenerators[rolenames.ROLE_PAGE_TAB]            = \
             self._getSpeechForPageTab
        self.speechGenerators[rolenames.ROLE_PAGE_TAB_LIST]       = \
             self._getSpeechForPageTabList
        self.speechGenerators[rolenames.ROLE_PASSWORD_TEXT]       = \
             self._getSpeechForText
        self.speechGenerators[rolenames.ROLE_PROGRESS_BAR]        = \
             self._getSpeechForProgressBar
        self.speechGenerators[rolenames.ROLE_PUSH_BUTTON]         = \
             self._getSpeechForPushButton
        self.speechGenerators[rolenames.ROLE_RADIO_BUTTON]        = \
             self._getSpeechForRadioButton
        self.speechGenerators[rolenames.ROLE_RADIO_MENU]          = \
             self._getSpeechForRadioMenuItem
        self.speechGenerators[rolenames.ROLE_RADIO_MENU_ITEM]     = \
             self._getSpeechForRadioMenuItem
        self.speechGenerators[rolenames.ROLE_ROW_HEADER]          = \
             self._getSpeechForRowHeader
        self.speechGenerators[rolenames.ROLE_SCROLL_BAR]          = \
             self._getSpeechForScrollBar
        self.speechGenerators[rolenames.ROLE_SLIDER]              = \
             self._getSpeechForSlider
        self.speechGenerators[rolenames.ROLE_SPIN_BUTTON]         = \
             self._getSpeechForSpinButton
        self.speechGenerators[rolenames.ROLE_SPLIT_PANE]          = \
             self._getSpeechForSplitPane
        self.speechGenerators[rolenames.ROLE_TABLE]               = \
             self._getSpeechForTable
        self.speechGenerators[rolenames.ROLE_TABLE_CELL]          = \
             self._getSpeechForTableCell
        self.speechGenerators[rolenames.ROLE_TABLE_COLUMN_HEADER] = \
             self._getSpeechForTableColumnHeader
        self.speechGenerators[rolenames.ROLE_TABLE_ROW_HEADER]    = \
             self._getSpeechForTableRowHeader
        self.speechGenerators[rolenames.ROLE_TEAR_OFF_MENU_ITEM]  = \
             self._getSpeechForMenu
        self.speechGenerators[rolenames.ROLE_TERMINAL]            = \
             self._getSpeechForTerminal
        self.speechGenerators[rolenames.ROLE_TEXT]                = \
             self._getSpeechForText
        self.speechGenerators[rolenames.ROLE_TOGGLE_BUTTON]       = \
             self._getSpeechForToggleButton
        self.speechGenerators[rolenames.ROLE_TOOL_BAR]            = \
             self._getSpeechForToolBar
        self.speechGenerators[rolenames.ROLE_TREE]                = \
             self._getSpeechForTable
        self.speechGenerators[rolenames.ROLE_TREE_TABLE]          = \
             self._getSpeechForTable
        self.speechGenerators[rolenames.ROLE_WINDOW]              = \
             self._getSpeechForWindow


    def _getSpeechForAccelerator(self, obj):
        """Returns a list of utterances that describes the keyboard
        accelerator (and possibly shortcut) for the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a list of utterances to be spoken.
        """
    
        result = a11y.getAcceleratorAndShortcut(obj)
    
        accelerator = result[0]
        #shortcut = result[1]

        utterances = []

        # [[[TODO: WDW - various stuff preserved while we work out the
        # desired verbosity here.]]]
        #
        #if len(shortcut) > 0:
        #    utterances.append(_("shortcut") + " " + shortcut)
        #    utterances.append(accelerator)
        if len(accelerator) > 0:
            #utterances += (_("accelerator") + " " + accelerator)
            utterances.append(accelerator)

        return utterances
    
    
    def _getSpeechForAvailability(self, obj):
        """Returns a list of utterances that describes the availability
        of the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a list of utterances to be spoken.
        """

        utterances = []
        if obj.state.count(core.Accessibility.STATE_SENSITIVE) == 0:
            utterances.append(_("grayed"))

        return utterances
    
    
    def _getSpeechForLabelAndRole(self, obj):
        """Returns the list of utteranaces to be spoken for the object's
        label and role.
    
        Arguments:
        - obj: an Accessible
    
        Returns a list of utterances to be spoken for the label and role.
        """
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        text = obj.label
        
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            text += " " + getSpeechForRoleName(obj)
    
        return [text]


    def _debugGenerator(self, generatorName, obj, already_focused, utterances):
        """Prints debug.LEVEL_FINER information regarding the speech generator.
    
        Arguments:
        - generatorName: the name of the generator
        - obj: the object being presented
        - already_focused: boolean stating if object just received focus
        - utterances: the generated text
        """
    
        debug.println(debug.LEVEL_FINER,
                      "GENERATOR: %s" % generatorName)
        debug.println(debug.LEVEL_FINER,
                      "           obj             = %s" % obj.name)
        debug.println(debug.LEVEL_FINER,
                      "           role            = %s" % obj.role)
        debug.println(debug.LEVEL_FINER,
                      "           already_focused = %s" % already_focused)
        debug.println(debug.LEVEL_FINER,
                      "           utterances:")
        for text in utterances:
            debug.println(debug.LEVEL_FINER,
                      "               (%s)" % text)


    def _getDefaultSpeech(self, obj, already_focused):
        """Gets a list of utterances to be spoken for the current
        object's name, role, and any accelerators.  This is usually the
        fallback speech generator should no other specialized speech
        generator exist for this object.

        The default speech will be of the following form:

        label [role] [accelerator] [availability]
        
        Arguments:
        - obj: an Accessible
        - already_focused: True if object just received focus; False otherwise
        
        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:
            utterances.extend(self._getSpeechForLabelAndRole(obj))
            utterances.extend(self._getSpeechForAvailability(obj))
        
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances be spoken.
        """
        
        utterances = self._getSpeechForLabelAndRole(obj)
    
        # Find all the unrelated labels in the dialog and speak them.
        #
        labels = a11y.findUnrelatedLabels(obj)
        for label in labels:
            utterances.append(label.name)
        
        self._debugGenerator("_getSpeechForAlert",
                             obj,
                             already_focused,
                             utterances)
        
        return utterances
    
    
    def _getSpeechForAnimation(self, obj, already_focused):
        """Gets the speech for an animation.
    
        Arguments:
        - obj: the animation
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken.
        """
        
        utterances = self._getSpeechForLabelAndRole(obj)
        
        if obj.description:
            utterances.append(obj.description)
    
        self._debugGenerator("_getSpeechForAnimation",
                             obj,
                             already_focused,
                             utterances)
        
        return utterances
    
    
    def _getSpeechForArrow(self, obj, already_focused):
        """Gets a list of utterances to be spoken for an arrow.
    
        Arguments:
        - obj: the arrow
        - already_focused: True if object just received focus; False otherwise
    
        Returns a list of utterances to be spoken for the object.
        """
    
        # [[[TODO: determine orientation of arrow.  Logged as bugzilla bug
        # 319744.]]]
        # text = arrow direction (left, right, up, down)
        #
        utterances = self._getSpeechForLabelAndRole(obj)
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        if obj.state.count(core.Accessibility.STATE_CHECKED):
            # If it's not already focused, say it's name
            #
            if not already_focused:
                tmp = self._getSpeechForLabelAndRole(obj)
                tmp.append(_("checked"))
                utterances.extend(tmp)
                utterances.extend(self._getSpeechForAvailability(obj))
            else:
                utterances.append(_("checked"))
        else:
            if not already_focused:
                tmp = self._getSpeechForLabelAndRole(obj)
                tmp.append(_("not checked"))
                utterances.extend(tmp)
                utterances.extend(self._getSpeechForAvailability(obj))
            else:
                utterances.append(_("not checked"))
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getSpeechForCheckBox(obj, False)
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.extend(self._getSpeechForAvailability(obj))
            utterances.extend(self._getSpeechForAccelerator(obj))
        
        self._debugGenerator("_getSpeechForCheckMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    
    def _getSpeechForColumnHeader(self, obj, already_focused):
        """Get the speech for a column header.
        
        Arguments:
        - obj: the column header
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        utterances = []
        if not already_focused:
            utterances.append(obj.label)
    
        # Find the text displayed in the combo box.  This is either:
        #
        # 1) The last text object that's a child of the combo box
        # 2) The selected child of the combo box.
        # 3) The contents of the text of the combo box itself when
        #    treated as a text object.
        #
        # Preference is given to #1, if it exists.
        #
        # [[[TODO: WDW - Combo boxes are complex beasts.  This algorithm
        # needs serious work.  Logged as bugzilla bug 319745.]]]
        #
        textObj = None
        for i in range(0, obj.childCount):
            debug.println(debug.LEVEL_FINEST,
                          "speechgenerator._getSpeechForComboBox " \
                          + "looking at child %d" % i)
            child = obj.child(i)
            if child.role == rolenames.ROLE_TEXT:
                textObj = child
    
        if textObj:
            result = a11y.getTextLineAtCaret(textObj)
            line = result[0]
            utterances.append(line)
        else:
            selectedItem = None
            comboSelection = obj.selection
            if comboSelection and comboSelection.nSelectedChildren > 0:
                selectedItem = a11y.makeAccessible(\
                    comboSelection.getSelectedChild(0))
            if selectedItem:
                utterances.append(selectedItem.label)
            else:
                result = a11y.getTextLineAtCaret(obj)
                selectedText = result[0]
                if len(selectedText) > 0:
                    utterances.append(selectedText)
                else:
                    debug.println(
                        debug.LEVEL_SEVERE,
                        "ERROR: Could not find selected item for combo box.")

        if not already_focused:
            if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                utterances.append(getSpeechForRoleName(obj))

        self._debugGenerator("_getSpeechForComboBox",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForDesktopIcon(self, obj, already_focused):
        """Get the speech for a desktop icon.
        
        Arguments:
        - obj: the desktop icon
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
    
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDirectoryPane",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances

    
    def _getSpeechForFrame(self, obj, already_focused):
        """Get the speech for a frame.
        
        Arguments:
        - obj: the frame
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """

        #utterances = self._getDefaultSpeech(obj, already_focused)
        utterances = self._getSpeechForAlert(obj, already_focused)
        
        self._debugGenerator("_getSpeechForFrame",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForHtmlContainer(self, obj, already_focused):
        """Get the speech for an HTML container.
        
        Arguments:
        - obj: the dial
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - HACK to remove availability output because nautilus
        # doesn't include this information for desktop icons.  If, at some
        # point, it is determined that availability should be added back in,
        # then a custom script for nautilus needs to be written to remove the
        # availability.]]]
        #
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label

        if obj.image:
            description = obj.image.imageDescription
            if len(description):
                if len(text):
                    text += " "
                text += description
                
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if len(text):
                text += " "
            text += getSpeechForRoleName(obj)
    
        self._debugGenerator("_getSpeechForIcon",
                             obj,
                             already_focused,
                             [text])

        return [text]
    
    
    def _getSpeechForImage(self, obj, already_focused):
        """Get the speech for an image.
        
        Arguments:
        - obj: the image
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForImage",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForLabel(self, obj, already_focused):
        """Get the speech for a label.
        
        Arguments:
        - obj: the label
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForLabel",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances

    
    def _getSpeechForList(self, obj, already_focused):
        """Get the speech for a list.
        
        Arguments:
        - obj: the list
        - already_focused: if False, the obj just received focus
    
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
    
    
    def _getSpeechForMenu(self, obj, already_focused):
        """Get the speech for a menu.
        
        Arguments:
        - obj: the menu
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getDefaultSpeech(obj, already_focused)
    
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        if (obj == orca.locusOfFocus) \
               and (verbosity == settings.VERBOSITY_LEVEL_VERBOSE):
            utterances.extend(self._getSpeechForAvailability(obj))
            utterances.extend(self._getSpeechForAccelerator(obj))
        
        self._debugGenerator("_getSpeechForMenu",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    def _getSpeechForMenuBar(self, obj, already_focused):
        """Get the speech for a menu bar.
        
        Arguments:
        - obj: the menu bar
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        utterances = [obj.label]
            
        # No need to say "menu item" because we already know that.
        #
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.extend(self._getSpeechForAvailability(obj))
            utterances.extend(self._getSpeechForAccelerator(obj))
        
        self._debugGenerator("_getSpeechForMenuItem",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForText(self, obj, already_focused):
        """Get the speech for a text component.
        
        Arguments:
        - obj: the text component
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        # [[[TODO: WDW - HACK to remove availability because some text
        # areas, such as those in yelp, come up as insensitive though
        # they really are ineditable.]]]
        #
        utterances = self._getSpeechForLabelAndRole(obj)

        result = a11y.getTextLineAtCaret(obj)
        utterances.append(result[0])
    
        self._debugGenerator("_getSpeechForText",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForOptionPane(self, obj, already_focused):
        """Get the speech for an option pane.
        
        Arguments:
        - obj: the option pane
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getDefaultSpeech(obj, already_focused)
        if obj.childCount == 1:
            utterances.append(_("one tab"))
        else:
            utterances.append(("%d " % obj.childCount) + _("tabs"))
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        percentage = ("%d" % obj.value.currentValue) + " " \
                     + _("percent") + ". "
        
        if not already_focused:
            utterances = self._getSpeechForLabelAndRole(obj)
            utterances.append(percentage)
        else:
            utterances = [percentage]
            
        self._debugGenerator("_getSpeechForProgressBar",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForPushButton(self, obj, already_focused):
        """Get the speech for a push button
        
        Arguments:
        - obj: the push button
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = []
        if obj.state.count(core.Accessibility.STATE_CHECKED):
            # If it's not already focused, say it's name
            #
            if not already_focused:
                tmp = self._getSpeechForLabelAndRole(obj)
                tmp.append(_("selected"))
                utterances.extend(tmp)
                utterances.extend(self._getSpeechForAvailability(obj))
            else:
                utterances.append(_("selected"))
        else:
            if not already_focused:
                tmp = self._getSpeechForLabelAndRole(obj)
                tmp.append(_("not selected"))
                utterances.extend(tmp)
                utterances.extend(self._getSpeechForAvailability(obj))
            else:
                utterances.append(_("not selected"))
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForRadioButton(obj, False)
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.extend(self._getSpeechForAvailability(obj))
            utterances.extend(self._getSpeechForAccelerator(obj))
        
        self._debugGenerator("_getSpeechForRadioMenuItem",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForRowHeader(self, obj, already_focused):
        """Get the speech for a row header.
        
        Arguments:
        - obj: the column header
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
    
        # [[[TODO: WDW - want to get orientation. Logged as bugzilla bug
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        value = obj.value
    
        # OK, this craziness is all about trying to figure out the most
        # meaningful formatting string for the floating point values.
        # The number of places to the right of the decimal point should
        # be set by the minimumIncrement, but the minimumIncrement isn't
        # always set.  So...we'll default the minimumIncrement to 1/100
        # of the range.  But, if max == min, then we'll just go for showing
        # them off to two meaningful digits.
        #
        try:
            minimumIncrement = value.minimumIncrement
        except:
            minimumIncrement = (value.maximumValue - value.minimumValue) \
                               / 100.0
    
        try:
            decimalPlaces = max(0, -math.log10(minimumIncrement))
        except:
            try:
                decimalPlaces = max(0, -math.log10(value.minimumValue))
            except:
                try:
                    decimalPlaces = max(0, -math.log10(value.maximumValue))
                except:
                    decimalPlaces = 0
    
        formatter = "%%.%df" % decimalPlaces
        valueString = formatter % value.currentValue
        #minString   = formatter % value.minimumValue
        #maxString   = formatter % value.maximumValue
    
        if already_focused:
            utterances = [valueString]
        else:
            utterances = self._getSpeechForLabelAndRole(obj)
            utterances.append(valueString)
            utterances.extend(self._getSpeechForAvailability(obj))
        
        self._debugGenerator("_getSpeechForProgressBar",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForSpinButton(self, obj, already_focused):
        """Get the speech for a spin button.  If the object already has
        focus, then only the new value is spoken.
        
        Arguments:
        - obj: the spin button
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
    
        if already_focused:
            utterances = []
        else:
            utterances = self._getDefaultSpeech(obj, already_focused)
            
        result = a11y.getTextLineAtCaret(obj)
        utterances.append(result[0])
    
        self._debugGenerator("_getSpeechForSpinButton",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForSplitPane(self, obj, already_focused):
        """Get the speech for a split pane.
        
        Arguments:
        - obj: the split pane
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForSplitPane",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForTable(self, obj, already_focused):
        """Get the speech for a table
        
        Arguments:
        - obj: the table
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTable",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell
        
        Arguments:
        - obj: the table
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = []

        # [[[TODO: WDW - Attempt to infer the cell type.  There's a
        # bunch of stuff we can do here, such as check the EXPANDABLE
        # state, check the NODE_CHILD_OF relation, etc.  Logged as
        # bugzilla bug 319750.]]]
        #
        action = obj.action
        if action:
            for i in range(0, action.nActions):
                debug.println(debug.LEVEL_FINEST,
                    "speechgenerator._getSpeechForTableCell " \
                    + "looking at action %d" % i)
                if action.getName(i) == "toggle":
                    obj.role = rolenames.ROLE_CHECK_BOX
                    utterances = self._getSpeechForCheckBox(obj,
                                                            already_focused)
                    obj.role = rolenames.ROLE_TABLE_CELL
                    break
                #elif action.getName(i) == "edit":
                #    utterances = self._getSpeechForText(obj, True)
                #    break

        if (len(utterances) == 0) and (not already_focused):
            utterances = [obj.label]
            
        # [[[TODO: WDW - HACK attempt to determine if this is a node;
        # if so, describe its state.]]]
        #
        if obj.state.count(core.Accessibility.STATE_EXPANDABLE):
            if obj.state.count(core.Accessibility.STATE_EXPANDED):            
                utterances.append(_("expanded"))
            else:
                utterances.append(_("collapsed"))

        self._debugGenerator("_getSpeechForTableCell",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForTableColumnHeader(self, obj, already_focused):
        """Get the speech for a table column header
        
        Arguments:
        - obj: the table column header
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances = [_("tear off menu item")]
        else:
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        label = None
        frame = a11y.getFrame(obj)
        if frame:
            label = frame.name
        if label is None:
            label = obj.label

        utterances = [label]
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.append(getSpeechForRoleName(obj))
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = []
        if obj.state.count(core.Accessibility.STATE_CHECKED):
            # If it's not already focused, say it's name
            #
            if not already_focused:
                tmp = self._getSpeechForLabelAndRole(obj)
                tmp.append(_("pressed"))
                utterances.extend(tmp)
                utterances.extend(self._getSpeechForAvailability(obj))
            else:
                utterances.append(_("pressed"))
        else:
            if not already_focused:
                tmp = self._getSpeechForLabelAndRole(obj)
                tmp.append(_("not pressed"))
                utterances.extend(tmp)
                utterances.extend(self._getSpeechForAvailability(obj))
            else:
                utterances.append(_("not pressed"))
    
        self._debugGenerator("_getSpeechForToggleButton",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForToolBar(self, obj, already_focused):
        """Get the speech for a tool bar
        
        Arguments:
        - obj: the tool bar
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
        Returns a list of utterances to be spoken for the object.
        """
        
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTreeTable",
                             obj,
                             already_focused,
                             utterances)
    
        return utterances
    
    
    def _getSpeechForTreeTable(self, obj, already_focused):
        """Get the speech for a tree table
        
        Arguments:
        - obj: the tree table
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: if False, the obj just received focus
    
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
        - already_focused: boolean stating if object just received focus

        Returns a list of utterances to be spoken.
        """

        if self.speechGenerators.has_key(obj.role):
            generator = self.speechGenerators[obj.role]
        else:
            generator = self._getDefaultSpeech

        return generator(obj, already_focused)


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

        if obj is None:
            return utterances

        if obj is stopAncestor:
            return utterances

        # We try to ignore fillers and panels without names.
        # [[[TODO: WDW - HACK sometimes table cells can be children
        # of table cells (see the "Browse" dialog of gnome-terminal
        # via "Edit" -> "Current Profile" -> "General" Tab ->
        # "Profile icon:" button -> "Browse..." button - each element
        # in the list is a compound table cell where the icon and
        # text are child table cells of the table cell).  So...
        # we happily ignore those as well.  One thing we might
        # want to do is treat the parent as a compound object.
        # Logged as bugzilla bug 319751.]]]
        #
        parent = obj.parent
        if parent \
            and (obj.role == rolenames.ROLE_TABLE_CELL) \
            and (parent.role == rolenames.ROLE_TABLE_CELL):
            parent = parent.parent
            
        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break
            if (parent.role != rolenames.ROLE_FILLER) \
                and (parent.role != rolenames.ROLE_SPLIT_PANE):
                if len(parent.label) > 0:
                    utterances.append(parent.label + " " \
                                      + getSpeechForRoleName(parent))
                elif parent.role != rolenames.ROLE_PANEL:
                    utterances.append(getSpeechForRoleName(parent))

            parent = parent.parent

        utterances.reverse()
        
        return utterances
