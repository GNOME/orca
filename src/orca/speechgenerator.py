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
    
    def __init__(self, region=None):

        # Set up a dictionary that maps role names to functions
        # that generate speech for objects that implement that role.
        #
        self.speechGenerators = {}
        self.speechGenerators["alert"]               = \
             self._getSpeechForAlert
        self.speechGenerators["animation"]           = \
             self._getSpeechForAnimation
        self.speechGenerators["arrow"]               = \
             self._getSpeechForArrow
        self.speechGenerators["check box"]           = \
             self._getSpeechForCheckBox
        self.speechGenerators["check menu"]          = \
             self._getSpeechForCheckMenuItem
        self.speechGenerators["check menu item"]     = \
             self._getSpeechForCheckMenuItem
        self.speechGenerators["column_header"]       = \
             self._getSpeechForColumnHeader
        self.speechGenerators["combo box"]           = \
             self._getSpeechForComboBox
        self.speechGenerators["desktop icon"]        = \
             self._getSpeechForDesktopIcon
        self.speechGenerators["dial"]                = \
             self._getSpeechForDial
        self.speechGenerators["dialog"]              = \
             self._getSpeechForDialog
        self.speechGenerators["directory pane"]      = \
             self._getSpeechForDirectoryPane
        self.speechGenerators["frame"]               = \
             self._getSpeechForFrame
        self.speechGenerators["html container"]      = \
             self._getSpeechForHtmlContainer
        self.speechGenerators["icon"]                = \
             self._getSpeechForIcon
        self.speechGenerators["image"]               = \
             self._getSpeechForImage
        self.speechGenerators["label"]               = \
             self._getSpeechForLabel
        self.speechGenerators["list"]                = \
             self._getSpeechForList
        self.speechGenerators["menu"]                = \
             self._getSpeechForMenu
        self.speechGenerators["menu bar"]            = \
             self._getSpeechForMenuBar
        self.speechGenerators["menu item"]           = \
             self._getSpeechForMenuItem
        self.speechGenerators["multi line text"]     = \
             self._getSpeechForText
        self.speechGenerators["option pane"]         = \
             self._getSpeechForOptionPane
        self.speechGenerators["page tab"]            = \
             self._getSpeechForPageTab
        self.speechGenerators["page tab list"]       = \
             self._getSpeechForPageTabList
        self.speechGenerators["password text"]       = \
             self._getSpeechForText
        self.speechGenerators["progress bar"]        = \
             self._getSpeechForProgressBar
        self.speechGenerators["push button"]         = \
             self._getSpeechForPushButton
        self.speechGenerators["radio button"]        = \
             self._getSpeechForRadioButton
        self.speechGenerators["radio menu"]          = \
             self._getSpeechForRadioMenuItem
        self.speechGenerators["radio menu item"]     = \
             self._getSpeechForRadioMenuItem
        self.speechGenerators["row_header"]          = \
             self._getSpeechForRowHeader
        self.speechGenerators["scroll bar"]          = \
             self._getSpeechForScrollBar
        self.speechGenerators["single line text"]    = \
             self._getSpeechForText
        self.speechGenerators["slider"]              = \
             self._getSpeechForSlider
        self.speechGenerators["spin button"]         = \
             self._getSpeechForSpinButton
        self.speechGenerators["split pane"]          = \
             self._getSpeechForSplitPane
        self.speechGenerators["table"]               = \
             self._getSpeechForTable
        self.speechGenerators["table cell"]          = \
             self._getSpeechForTableCell
        self.speechGenerators["table column header"] = \
             self._getSpeechForTableColumnHeader
        self.speechGenerators["table row header"]    = \
             self._getSpeechForTableRowHeader
        self.speechGenerators["tear off menu item"]  = \
             self._getSpeechForMenu
        self.speechGenerators["terminal"]            = \
             self._getSpeechForTerminal
        self.speechGenerators["text"]                = \
             self._getSpeechForText
        self.speechGenerators["toggle button"]       = \
             self._getSpeechForToggleButton
        self.speechGenerators["tool bar"]            = \
             self._getSpeechForToolBar
        self.speechGenerators["tree"]                = \
             self._getSpeechForTable
        self.speechGenerators["tree table"]          = \
             self._getSpeechForTable
        self.speechGenerators["window"]              = \
             self._getSpeechForWindow


    def _getSpeechForAccelerator(self, obj):
        """Returns a string to be spoken that describes the keyboard
        accelerator (and possibly shortcut) for the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a string to be spoken.
        """
    
        result = a11y.getAcceleratorAndShortcut(obj)
    
        accelerator = result[0]
        shortcut = result[1]
    
        if len(shortcut) > 0:
            text += _("shortcut") + " " + shortcut + ". "
        if len(accelerator) > 0:
            text += _("accelerator") + " " + accelerator + ". "
            
        return text
    
    
    def _getSpeechForAvailability(self, obj):
        """Returns a string to be spoken that describes the availability
        of the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a string to be spoken.
        """
        
        if obj.state.count(core.Accessibility.STATE_SENSITIVE):
            return ""
        else:
            return _("unavailable") + ". "
    
    
    def _getSpeechForLabelAndRole(self, obj):
        """Returns the text to be spoken for the object's label and role.
    
        Arguments:
        - obj: an Accessible
    
        Returns a sentence for the label and role.
        """
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        text = obj.label
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            text += " " + getSpeechForRoleName(obj)
    
        text += ". "
        
        return text


    def _debugGenerator(self, generatorName, obj, already_focused, text):
        """Prints debug.LEVEL_FINER information regarding the speech generator.
    
        Arguments:
        - generatorName: the name of the generator
        - obj: the object being presented
        - already_focused: boolean stating if object just received focus
        - text: the generated text
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
                      "           text            = %s" % text)    


    def _getDefaultSpeech(self, obj, already_focused):
        """Gets text to be spoken for the current object's name, role, and
        any accelerators.  This is usually the fallback speech generator
        should no other specialized speech generator exist for this object.

        The default speech will be of the following form:

        label [role] [accelerator] [availability]
        
        Arguments:
        - obj: an Accessible
        - already_focused: True if object just received focus; False otherwise
        
        Returns text to be spoken for the object.
        """
    
        text = self._getSpeechForLabelAndRole(obj) \
               + self._getSpeechForAvailability(obj)
        
        text = text.replace("...", _(" dot dot dot"), 1)
    
        self._debugGenerator("_getDefaultSpeech",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForAlert(self, obj, already_focused):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.
    
        Arguments:
        - obj: the Accessible dialog
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken.
        """
        
        text = self._getSpeechForLabelAndRole(obj)
    
        # Find all the labels in the dialog
        #
        labels = a11y.findByRole(obj, "label")
    
        # Add the names of only those labels which are not associated with
        # other objects (i.e., empty relation sets).  [[[TODO: WDW - HACK:
        # In addition, do not grab free labels whose parents are push buttons
        # because push buttons can have labels as children.]]]
        #
        for label in labels:
            set = label.relations
            if len(set) == 0:
                parent = label.parent
                if parent and (parent.role == rolenames.ROLE_PUSH_BUTTON):
                    pass
                else:
                    set = label.state
                    if set.count(core.Accessibility.STATE_SHOWING):
                        text += " " + label.name
            
        self._debugGenerator("_getSpeechForAlert",
                             obj,
                             already_focused,
                             text)
        
        return text
    
    
    def _getSpeechForAnimation(self, obj, already_focused):
        """Gets the speech for an animation.
    
        Arguments:
        - obj: the animation
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken.
        """
        
        text = self._getSpeechForLabelAndRole(obj) + ". "
        
        if obj.description:
            text += obj.description + ". "
    
        self._debugGenerator("_getSpeechForAnimation",
                             obj,
                             already_focused,
                             text)
        
        return text
    
    
    def _getSpeechForArrow(self, obj, already_focused):
        """Gets text to be spoken for an arrow.
    
        Arguments:
        - obj: the arrow
        - already_focused: True if object just received focus; False otherwise
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: determine orientation of arrow.]]]
        # text = arrow direction (left, right, up, down)
        #
        text = self._getSpeechForLabelAndRole(obj)
    
        self._debugGenerator("_getSpeechForArrow",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForCheckBox(self, obj, already_focused):
        """Get the speech for a check box.  If the check box already had
        focus, then only the state is spoken.
        
        Arguments:
        - obj: the check box
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            # If it's not already focused, say it's name
            #
            if already_focused == False:
                text = self._getSpeechForLabelAndRole(obj) \
                       + _("checked") + ". " \
                       + self._getSpeechForAvailability(obj)
            else:
                text = _("checked") + ". "
        else:
            if already_focused == False:
                text = self._getSpeechForLabelAndRole(obj) \
                       + _("not checked") + ". " \
                       + self._getSpeechForAvailability(obj)
            else:
                text = _("not checked") + ". "
    
        self._debugGenerator("_getSpeechForCheckBox",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForCheckMenuItem(self, obj, already_focused):
        """Get the speech for a check menu item.  If the check menu item
        already had focus, then only the state is spoken.
        
        Arguments:
        - obj: the check menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getSpeechForCheckBox(obj, False)
        
        self._debugGenerator("_getSpeechForCheckMenuItem",
                             obj,
                             already_focused,
                             text)

        return text

    
    def _getSpeechForColumnHeader(self, obj, already_focused):
        """Get the speech for a column header.
        
        Arguments:
        - obj: the column header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForColumnHeader",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForComboBox(self, obj, already_focused):
        """Get the speech for a combo box.  If the combo box already has focus,
        then only the selection is spoken.
        
        Arguments:
        - obj: the combo box
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        if already_focused:
            text = ""
        else:
            text = self._getSpeechForLabelAndRole(obj)
    
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
        # needs serious work.]]]
        #
        textObj = None
        childCount = obj.childCount
        i = 0
        while i < childCount:
            child = obj.child(i)
            if child.role == rolenames.ROLE_TEXT:
                textObj = child
            i = i + 1
    
        if textObj:
            result = a11y.getTextLineAtCaret(textObj)
            line = result[0]    
            text += line + ". "
        else:
            selectedItem = None
            comboSelection = obj.selection
            if comboSelection and comboSelection.nSelectedChildren > 0:
                selectedItem = a11y.makeAccessible(\
                    comboSelection.getSelectedChild(0))
            if selectedItem:
                text += selectedItem.label + ". "
            else:
                result = a11y.getTextLineAtCaret(obj)
                selectedText = result[0]
                if len(selectedText) > 0:
                    text += selectedText + ". "
                else:
                    debug.println(
                        debug.LEVEL_SEVERE,
                        "ERROR: Could not find selected item for combo box.")
    
        self._debugGenerator("_getSpeechForComboBox",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForDesktopIcon(self, obj, already_focused):
        """Get the speech for a desktop icon.
        
        Arguments:
        - obj: the desktop icon
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForDesktopIcon",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForDial(self, obj, already_focused):
        """Get the speech for a dial.
        
        Arguments:
        - obj: the dial
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: WDW - might need to include the value here?]]]
        #
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForDial",
                             obj,
                             already_focused,
                             text)

        return text
    
    
    def _getSpeechForDialog(self, obj, already_focused):
        """Get the speech for a dialog box.
        
        Arguments:
        - obj: the dialog box
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getSpeechForAlert(obj, already_focused)
    
        self._debugGenerator("_getSpeechForDialog",
                             obj,
                             already_focused,
                             text)

        return text
    
    
    def _getSpeechForDirectoryPane(self, obj, already_focused):
        """Get the speech for a directory pane.
        
        Arguments:
        - obj: the dial
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
    
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDirectoryPane",
                             obj,
                             already_focused,
                             text)
    
        return text

    
    def _getSpeechForFrame(self, obj, already_focused):
        """Get the speech for a frame.
        
        Arguments:
        - obj: the frame
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForFrame",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForHtmlContainer(self, obj, already_focused):
        """Get the speech for an HTML container.
        
        Arguments:
        - obj: the dial
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForHtmlContainer",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForIcon(self, obj, already_focused):
        """Get the speech for an icon.
        
        Arguments:
        - obj: the icon
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        # [[[TODO: WDW - HACK to remove availability output because nautilus
        # doesn't include this information for desktop icons.  If, at some
        # point, it is determined that availability should be added back in,
        # then a custom script for nautilus needs to be written to remove the
        # availability.]]]
        #
        text = self._getSpeechForLabelAndRole(obj)
        
        self._debugGenerator("_getSpeechForIcon",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForImage(self, obj, already_focused):
        """Get the speech for an image.
        
        Arguments:
        - obj: the image
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForImage",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForLabel(self, obj, already_focused):
        """Get the speech for a label.
        
        Arguments:
        - obj: the label
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForLabel",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForList(self, obj, already_focused):
        """Get the speech for a list.
        
        Arguments:
        - obj: the list
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: WDW - include how many items in the list?]]]
        #
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForList",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForMenu(self, obj, already_focused):
        """Get the speech for a menu.
        
        Arguments:
        - obj: the menu
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
    
        #i = 0
        #itemCount = 0
        #while i < obj.childCount:
        #    child = obj.child(i)
        #    if child.role != rolenames.ROLE_SEPARATOR:
        #        itemCount += 1
        #    i += 1
        #            
        #if itemCount == 1:
        #    text += _("one item") + ". "
        #else:
        #    text += ("%d " % itemCount) + _("items") + ". "
    
        self._debugGenerator("_getSpeechForMenu",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    def _getSpeechForMenuBar(self, obj, already_focused):
        """Get the speech for a menu bar.
        
        Arguments:
        - obj: the menu bar
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForMenuBar",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForMenuItem(self, obj, already_focused):
        """Get the speech for a menu item.
        
        Arguments:
        - obj: the menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForMenuItem",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForText(self, obj, already_focused):
        """Get the speech for a text component.
        
        Arguments:
        - obj: the text component
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        result = a11y.getTextLineAtCaret(obj)
        text += result[0]
    
        self._debugGenerator("_getSpeechForText",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForOptionPane(self, obj, already_focused):
        """Get the speech for an option pane.
        
        Arguments:
        - obj: the option pane
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForOptionPane",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForPageTab(self, obj, already_focused):
        """Get the speech for a page tab.
        
        Arguments:
        - obj: the page tab
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForPageTab",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForPageTabList(self, obj, already_focused):
        """Get the speech for a page tab list.
        
        Arguments:
        - obj: the page tab list
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        if obj.childCount == 1:
            text += _("one tab") + ". "
        else:
            text += ("%d " % tablist.childCount) + _("tabs") + ". "
    
        self._debugGenerator("_getSpeechForPageTabList",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForProgressBar(self, obj, already_focused):
        """Get the speech for a progress bar.  If the object already
        had focus, just the new value is spoken.
        
        Arguments:
        - obj: the progress bar
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        value = obj.value
        percentage = ("%d" % obj.value.currentValue) + " " \
                     + _("percent") + ". "
        
        if already_focused == False:
            text = self._getSpeechForLabelAndRole(obj) \
                   + percentage
        else:
            text = percentage
            
        self._debugGenerator("_getSpeechForProgressBar",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForPushButton(self, obj, already_focused):
        """Get the speech for a push button
        
        Arguments:
        - obj: the push button
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForPushButton",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForRadioButton(self, obj, already_focused):
        """Get the speech for a radio button.  If the button already had
        focus, then only the state is spoken.
        
        Arguments:
        - obj: the check box
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            # If it's not already focused, say it's name
            #
            if already_focused == False:
                text = self._getSpeechForLabelAndRole(obj) \
                       + _("selected") + ". " \
                       + self._getSpeechForAvailability(obj)
            else:
                text = _("selected") + ". "
        else:
            if already_focused == False:
                text = self._getSpeechForLabelAndRole(obj) \
                       + _("not selected") + ". " \
                       + self._getSpeechForAvailability(obj)
            else:
                text = _("not selected") + ". "
    
        self._debugGenerator("_getSpeechForRadioButton",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForRadioMenuItem(self, obj, already_focused):
        """Get the speech for a radio menu item.  If the menu item
        already had focus, then only the state is spoken.
        
        Arguments:
        - obj: the check menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getSpeechForRadioButton(obj, False)
        
        self._debugGenerator("_getSpeechForRadioMenuItem",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForRowHeader(self, obj, already_focused):
        """Get the speech for a row header.
        
        Arguments:
        - obj: the column header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForRowHeader",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForScrollBar(self, obj, already_focused):
        """Get the speech for a scroll bar.
        
        Arguments:
        - obj: the scroll bar
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: WDW - want to get orientation.]]]
        #
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForScrollBar",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForSlider(self, obj, already_focused):
        """Get the speech for a slider.  If the object already
        had focus, just the value is spoken.
        
        Arguments:
        - obj: the slider
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
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
                decimalPlaces = max(0, -math.log10(minimumValue))
            except:
                try:
                    decimalPlaces = max(0, -math.log10(maximumValue))
                except:
                    decimalPlaces = 0
    
        formatter = "%%.%df" % decimalPlaces
        valueString = formatter % value.currentValue
        minString   = formatter % value.minimumValue
        maxString   = formatter % value.maximumValue
    
        if already_focused:
            text = valueString
        else:
            text = self._getSpeechForLabelAndRole(obj) + valueString + ". " \
                   + self._getSpeechForAvailability(obj)
        
        self._debugGenerator("_getSpeechForProgressBar",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForSpinButton(self, obj, already_focused):
        """Get the speech for a spin button.  If the object already has
        focus, then only the new value is spoken.
        
        Arguments:
        - obj: the spin button
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
    
        if already_focused:
            text = ""
        else:
            text = self._getDefaultSpeech(obj, already_focused)
            
        result = a11y.getTextLineAtCaret(obj)
        text += result[0] + ". "
    
        self._debugGenerator("_getSpeechForSpinButton",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForSplitPane(self, obj, already_focused):
        """Get the speech for a split pane.
        
        Arguments:
        - obj: the split pane
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForSplitPane",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTable(self, obj, already_focused):
        """Get the speech for a table
        
        Arguments:
        - obj: the table
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTable",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell
        
        Arguments:
        - obj: the table
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForTableCell",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTableColumnHeader(self, obj, already_focused):
        """Get the speech for a table column header
        
        Arguments:
        - obj: the table column header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getSpeechForColumnHeader(obj, already_focused)
        
        self._debugGenerator("_getSpeechForTableColumnHeader",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTableRowHeader(self, obj, already_focused):
        """Get the speech for a table row header
        
        Arguments:
        - obj: the table row header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getSpeechForRowHeader(obj, already_focused)
        
        self._debugGenerator("_getSpeechForTableRowHeader",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTearOffMenuItem(self, obj, already_focused):
        """Get the speech for a tear off menu item
        
        Arguments:
        - obj: the tear off menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            text = _("tear off menu item")
        else:
            text = _("tear off")
    
        text += ". "
        
        self._debugGenerator("_getSpeechForTearOffMenuItem",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTerminal(self, obj, already_focused):
        """Get the speech for a terminal
        
        Arguments:
        - obj: the terminal
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = ""
    
        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        label = None
        frame = a11y.getFrame(obj)
        if frame:
            label = frame.name
        if label is None:
            label = obj.label
        text = label
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            text += " " + getSpeechForRoleName(obj)
    
        text += ". "
        
        self._debugGenerator("_getSpeechForTerminal",
                             obj,
                             already_focused,
                             text)
            
        return text
    
    
    def _getSpeechForToggleButton(self, obj, already_focused):
        """Get the speech for a toggle button.  If the toggle button already
        had focus, then only the state is spoken.
        
        Arguments:
        - obj: the check box
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        set = obj.state
        if set.count(core.Accessibility.STATE_PRESSED) \
               or set.count(core.Accessibility.STATE_CHECKED):
            # If it's not already focused, say it's name
            #
            if already_focused == False:
                text = self._getSpeechForLabelAndRole(obj) \
                       + _("pressed") + ". " \
                       + self._getSpeechForAvailability(obj)
            else:
                text = _("pressed") + ". "
        else:
            if already_focused == False:
                text = self._getSpeechForLabelAndRole(obj) \
                       + _("not pressed") + ". " \
                       + self._getSpeechForAvailability(obj)
            else:
                text = _("not pressed") + ". "
    
        self._debugGenerator("_getSpeechForToggleButton",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForToolBar(self, obj, already_focused):
        """Get the speech for a tool bar
        
        Arguments:
        - obj: the tool bar
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForToolBar",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTree(self, obj, already_focused):
        """Get the speech for a tree
        
        Arguments:
        - obj: the tree
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTreeTable",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForTreeTable(self, obj, already_focused):
        """Get the speech for a tree table
        
        Arguments:
        - obj: the tree table
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self._getDefaultSpeech(obj, already_focused)
        
        self._debugGenerator("_getSpeechForTreeTable",
                             obj,
                             already_focused,
                             text)
    
        return text
    
    
    def _getSpeechForWindow(self, obj, already_focused):
        """Get the speech for a window
        
        Arguments:
        - obj: the window
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForWindow",
                             obj,
                             already_focused,
                             text)
    
        return text


    def getSpeech(self, obj, already_focused):
        """Get the speech for an Accessible object.  This will look
        first to the specific speech generators and then to the
        default speech generator.  This method is the primary method
        that external callers of this class should use.
    
        Arguments:
        - obj: the object
        - already_focused: boolean staing if object just received focus

        Returns text to be spoken.
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
          
        Returns a string to be spoken.
        """

        text = ""

        if obj is None:
            return text

        if obj is stopAncestor:
            return text
        
        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break
            if len(parent.label) > 0:
                text = parent.label + " " \
                       + getSpeechForRoleName(parent) + " " + text
            elif (parent.role != rolenames.ROLE_PANEL) \
                     and (parent.role != rolenames.ROLE_FILLER):
                text = getSpeechForRoleName(parent) + " " + text
            parent = parent.parent
            
        return text
