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
        self.speechGenerators = {}
        self.speechGenerators["alert"]               = \
             self.getSpeechForAlert
        self.speechGenerators["animation"]           = \
             self.getSpeechForAnimation
        self.speechGenerators["arrow"]               = \
             self.getSpeechForArrow
        self.speechGenerators["check box"]           = \
             self.getSpeechForCheckBox
        self.speechGenerators["check menu item"]     = \
             self.getSpeechForCheckMenuItem
        self.speechGenerators["column_header"]       = \
             self.getSpeechForColumnHeader
        self.speechGenerators["combo box"]           = \
             self.getSpeechForComboBox
        self.speechGenerators["desktop icon"]        = \
             self.getSpeechForDesktopIcon
        self.speechGenerators["dial"]                = \
             self.getSpeechForDial
        self.speechGenerators["dialog"]              = \
             self.getSpeechForDialog
        self.speechGenerators["directory pane"]      = \
             self.getSpeechForDirectoryPane
        self.speechGenerators["frame"]               = \
             self.getSpeechForFrame
        self.speechGenerators["html container"]      = \
             self.getSpeechForHtmlContainer
        self.speechGenerators["icon"]                = \
             self.getSpeechForIcon
        self.speechGenerators["image"]               = \
             self.getSpeechForImage
        self.speechGenerators["label"]               = \
             self.getSpeechForLabel
        self.speechGenerators["list"]                = \
             self.getSpeechForList
        self.speechGenerators["menu"]                = \
             self.getSpeechForMenu
        self.speechGenerators["menu bar"]            = \
             self.getSpeechForMenuBar
        self.speechGenerators["menu item"]           = \
             self.getSpeechForMenuItem
        self.speechGenerators["multi line text"]     = \
             self.getSpeechForText
        self.speechGenerators["option pane"]         = \
             self.getSpeechForOptionPane
        self.speechGenerators["page tab"]            = \
             self.getSpeechForPageTab
        self.speechGenerators["page tab list"]       = \
             self.getSpeechForPageTabList
        self.speechGenerators["password text"]       = \
             self.getSpeechForText
        self.speechGenerators["progress bar"]        = \
             self.getSpeechForProgressBar
        self.speechGenerators["push button"]         = \
             self.getSpeechForPushButton
        self.speechGenerators["radio button"]        = \
             self.getSpeechForRadioButton
        self.speechGenerators["radio menu item"]     = \
             self.getSpeechForRadioMenuItem
        self.speechGenerators["row_header"]          = \
             self.getSpeechForRowHeader
        self.speechGenerators["scroll bar"]          = \
             self.getSpeechForScrollBar
        self.speechGenerators["single line text"]    = \
             self.getSpeechForText
        self.speechGenerators["slider"]              = \
             self.getSpeechForSlider
        self.speechGenerators["spin button"]         = \
             self.getSpeechForSpinButton
        self.speechGenerators["split pane"]          = \
             self.getSpeechForSplitPane
        self.speechGenerators["table"]               = \
             self.getSpeechForTable
        self.speechGenerators["table cell"]          = \
             self.getSpeechForTableCell
        self.speechGenerators["table column header"] = \
             self.getSpeechForTableColumnHeader
        self.speechGenerators["table row header"]    = \
             self.getSpeechForTableRowHeader
        self.speechGenerators["tear off menu item"]  = \
             self.getSpeechForMenu
        self.speechGenerators["terminal"]            = \
             self.getSpeechForTerminal
        self.speechGenerators["text"]                = \
             self.getSpeechForText
        self.speechGenerators["toggle button"]       = \
             self.getSpeechForToggleButton
        self.speechGenerators["tool bar"]            = \
             self.getSpeechForToolBar
        self.speechGenerators["tree"]                = \
             self.getSpeechForTable
        self.speechGenerators["tree table"]          = \
             self.getSpeechForTable
        self.speechGenerators["window"]              = \
             self.getSpeechForWindow


    def getSpeechForAccelerator(self, obj):
        """Returns a string to be spoken that describes the keyboard
        accelerator (and possibly shortcut) for the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a string to be spoken.
        """
    
        speakAccelerators = settings.getSetting("speakAccelerators",
                                                settings.ACCELERATOR_LONG)
    
        text = ""
        if not speakAccelerators == settings.ACCELERATOR_NONE:
            return text
        
        result = a11y.getAcceleratorAndShortcut(obj)
    
        accelerator = result[0]
        shortcut = result[1]
    
        if len(shortcut) > 0:
            text += _("shortcut") + " " + shortcut + ". "
        if len(accelerator) > 0:
            text += _("accelerator") + " " + accelerator + ". "
            
        return text
    
    
    def getSpeechForAvailability(self, obj):
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
    
    
    def getSpeechForLabelAndRole(self, obj):
        """Returns the text to be spoken for the object's label and role.
    
        Arguments:
        - obj: an Accessible
    
        Returns a sentence for the label and role.
        """
        
        speakRolenames = settings.getSetting("speakRolenames",
                                             settings.ROLENAME_LONG)
    
        text = obj.label
            
        if not speakRolenames == settings.ROLENAME_NONE:
            text += " " + getSpeechForRoleName(obj)
    
        text += ". "
        
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
            generator = self.getDefaultSpeech

        return generator(obj, already_focused)


    def debugGenerator(self, generatorName, obj, already_focused, text):
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
    
    
    def getDefaultSpeech(self, obj, already_focused):
        """Gets text to be spoken for the current object's name, role, and
        any accelerators.  This is usually the fallback speech generator
        should no other specialized speech generator exist for this object.
    
        Arguments:
        - obj: an Accessible
        - already_focused: True if object just received focus; False otherwise
        
        Returns text to be spoken for the object.
        """
    
        text = self.getSpeechForLabelAndRole(obj) \
               + self.getSpeechForAccelerator(obj) \
               + self.getSpeechForAvailability(obj)
        
        text = text.replace("...", _(" dot dot dot"), 1)
    
        self.debugGenerator("getDefaultSpeech",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForAlert(self, obj, already_focused):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.
    
        Arguments:
        - obj: the Accessible dialog
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken.
        """
        
        text = self.getSpeechForLabelAndRole(obj)
    
        # Find all the labels in the dialog
        #
        labels = a11y.findByRole(obj, "label")
    
        # Add the names of only those labels which are not associated with
        # other objects (i.e., empty relation sets)
        #
        for label in labels:
            set = label.relations
            if len(set) == 0:
                text += " " + label.name
    
        self.debugGenerator("getSpeechForAlert",
                            obj,
                            already_focused,
                            text)
        
        return text
    
    
    def getSpeechForAnimation(self, obj, already_focused):
        """Gets the speech for an animation.
    
        Arguments:
        - obj: the animation
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken.
        """
        
        text = self.getSpeechForLabelAndRole(obj)
        
        if obj.description:
            text += obj.description + ". "
    
        self.debugGenerator("getSpeechForAnimation",
                            obj,
                            already_focused,
                            text)
        
        return text
    
    
    def getSpeechForArrow(self, obj, already_focused):
        """Gets text to be spoken for an arrow.
    
        Arguments:
        - obj: the arrow
        - already_focused: True if object just received focus; False otherwise
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: determine orientation of arrow.]]]
        # text = arrow direction (left, right, up, down)
        #
        text = self.getSpeechForLabelAndRole(obj)
    
        self.debugGenerator("getSpeechForArrow",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForCheckBox(self, obj, already_focused):
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
                text = self.getSpeechForLabelAndRole(obj) \
                       + _("checked") + ". " \
                       + self.getSpeechForAccelerator(obj) \
                       + self.getSpeechForAvailability(obj)
            else:
                text = _("checked") + ". "
        else:
            if already_focused == False:
                text = self.getSpeechForLabelAndRole(obj) \
                       + _("not checked") + ". " \
                       + self.getSpeechForAccelerator(obj) \
                       + self.getSpeechForAvailability(obj)
            else:
                text = _("not checked") + ". "
    
        self.debugGenerator("getSpeechForCheckBox",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForCheckMenuItem(self, obj, already_focused):
        """Get the speech for a check menu item.  If the check menu item
        already had focus, then only the state is spoken.
        
        Arguments:
        - obj: the check menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getSpeechForCheckBox(obj, False)
        
        self.debugGenerator("getSpeechForCheckMenuItem",
                            obj,
                            already_focused,
                            text)

        return text

    
    def getSpeechForColumnHeader(self, obj, already_focused):
        """Get the speech for a column header.
        
        Arguments:
        - obj: the column header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForColumnHeader",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForComboBox(self, obj, already_focused):
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
            text = self.getSpeechForLabelAndRole(obj)
    
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
    
        self.debugGenerator("getSpeechForComboBox",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForDesktopIcon(self, obj, already_focused):
        """Get the speech for a desktop icon.
        
        Arguments:
        - obj: the desktop icon
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForDesktopIcon",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForDial(self, obj, already_focused):
        """Get the speech for a dial.
        
        Arguments:
        - obj: the dial
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: WDW - might need to include the value here?]]]
        #
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForDial",
                            obj,
                            already_focused,
                            text)

        return text
    
    
    def getSpeechForDialog(self, obj, already_focused):
        """Get the speech for a dialog box.
        
        Arguments:
        - obj: the dialog box
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getSpeechForAlert(obj, already_focused)
    
        self.debugGenerator("getSpeechForDialog",
                            obj,
                            already_focused,
                            text)

        return text
    
    
    def getSpeechForDirectoryPane(self, obj, already_focused):
        """Get the speech for a directory pane.
        
        Arguments:
        - obj: the dial
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
    
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForDirectoryPane",
                            obj,
                            already_focused,
                            text)
    
        return text

    
    def getSpeechForFrame(self, obj, already_focused):
        """Get the speech for a frame.
        
        Arguments:
        - obj: the frame
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForFrame",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForHtmlContainer(self, obj, already_focused):
        """Get the speech for an HTML container.
        
        Arguments:
        - obj: the dial
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForHtmlContainer",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForIcon(self, obj, already_focused):
        """Get the speech for an icon.
        
        Arguments:
        - obj: the icon
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForIcon",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForImage(self, obj, already_focused):
        """Get the speech for an image.
        
        Arguments:
        - obj: the image
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForImage",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForLabel(self, obj, already_focused):
        """Get the speech for a label.
        
        Arguments:
        - obj: the label
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForLabel",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForList(self, obj, already_focused):
        """Get the speech for a list.
        
        Arguments:
        - obj: the list
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: WDW - include how many items in the list?]]]
        #
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForList",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForMenu(self, obj, already_focused):
        """Get the speech for a menu.
        
        Arguments:
        - obj: the menu
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
    
        i = 0
        itemCount = 0
        while i < obj.childCount:
            child = obj.child(i)
            if child.role != rolenames.ROLE_SEPARATOR:
                itemCount += 1
            i += 1
                    
        if itemCount == 1:
            text += _("one item") + ". "
        else:
            text += ("%d " % itemCount) + _("items") + ". "
    
        self.debugGenerator("getSpeechForMenu",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    def getSpeechForMenuBar(self, obj, already_focused):
        """Get the speech for a menu bar.
        
        Arguments:
        - obj: the menu bar
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForMenuBar",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForMenuItem(self, obj, already_focused):
        """Get the speech for a menu item.
        
        Arguments:
        - obj: the menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForMenuItem",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForText(self, obj, already_focused):
        """Get the speech for a text component.
        
        Arguments:
        - obj: the text component
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        result = a11y.getTextLineAtCaret(obj)
        text += result[0]
    
        self.debugGenerator("getSpeechForText",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForOptionPane(self, obj, already_focused):
        """Get the speech for an option pane.
        
        Arguments:
        - obj: the option pane
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForOptionPane",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForPageTab(self, obj, already_focused):
        """Get the speech for a page tab.
        
        Arguments:
        - obj: the page tab
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForPageTab",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForPageTabList(self, obj, already_focused):
        """Get the speech for a page tab list.
        
        Arguments:
        - obj: the page tab list
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        if obj.childCount == 1:
            text += _("one tab") + ". "
        else:
            text += ("%d " % tablist.childCount) + _("tabs") + ". "
    
        self.debugGenerator("getSpeechForPageTabList",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForProgressBar(self, obj, already_focused):
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
            text = self.getSpeechForLabelAndRole(obj) \
                   + percentage
        else:
            text = percentage
            
        self.debugGenerator("getSpeechForProgressBar",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForPushButton(self, obj, already_focused):
        """Get the speech for a push button
        
        Arguments:
        - obj: the push button
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForPushButton",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForRadioButton(self, obj, already_focused):
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
                text = self.getSpeechForLabelAndRole(obj) \
                       + _("selected") + ". " \
                       + self.getSpeechForAccelerator(obj) \
                       + self.getSpeechForAvailability(obj)
            else:
                text = _("selected") + ". "
        else:
            if already_focused == False:
                text = self.getSpeechForLabelAndRole(obj) \
                       + _("not selected") + ". " \
                       + self.getSpeechForAccelerator(obj) \
                       + self.getSpeechForAvailability(obj)
            else:
                text = _("not selected") + ". "
    
        self.debugGenerator("getSpeechForRadioButton",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForRadioMenuItem(self, obj, already_focused):
        """Get the speech for a radio menu item.  If the menu item
        already had focus, then only the state is spoken.
        
        Arguments:
        - obj: the check menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getSpeechForRadioButton(obj, False)
        
        self.debugGenerator("getSpeechForRadioMenuItem",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForRowHeader(self, obj, already_focused):
        """Get the speech for a row header.
        
        Arguments:
        - obj: the column header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForRowHeader",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForScrollBar(self, obj, already_focused):
        """Get the speech for a scroll bar.
        
        Arguments:
        - obj: the scroll bar
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
    
        # [[[TODO: WDW - want to get orientation.]]]
        #
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForScrollBar",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForSlider(self, obj, already_focused):
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
            text = self.getSpeechForLabelAndRole(obj) + valueString + ". " \
                   + self.getSpeechForAccelerator(obj) \
                   + self.getSpeechForAvailability(obj)
        
        self.debugGenerator("getSpeechForProgressBar",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForSpinButton(self, obj, already_focused):
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
            text = self.getDefaultSpeech(obj, already_focused)
            
        result = a11y.getTextLineAtCaret(obj)
        text += result[0] + ". "
    
        self.debugGenerator("getSpeechForSpinButton",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForSplitPane(self, obj, already_focused):
        """Get the speech for a split pane.
        
        Arguments:
        - obj: the split pane
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForSplitPane",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTable(self, obj, already_focused):
        """Get the speech for a table
        
        Arguments:
        - obj: the table
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForTable",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell
        
        Arguments:
        - obj: the table
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForTableCell",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTableColumnHeader(self, obj, already_focused):
        """Get the speech for a table column header
        
        Arguments:
        - obj: the table column header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getSpeechForColumnHeader(obj, already_focused)
        
        self.debugGenerator("getSpeechForTableColumnHeader",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTableRowHeader(self, obj, already_focused):
        """Get the speech for a table row header
        
        Arguments:
        - obj: the table row header
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getSpeechForRowHeader(obj, already_focused)
        
        self.debugGenerator("getSpeechForTableRowHeader",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTearOffMenuItem(self, obj, already_focused):
        """Get the speech for a tear off menu item
        
        Arguments:
        - obj: the tear off menu item
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        speakRolenames = settings.getSetting("speakRolenames",
                                             settings.ROLENAME_LONG)
        
        if not speakRolenames == settings.ROLENAME_NONE:
            text = _("tear off menu item")
        else:
            text = _("tear off")
    
        text += ". "
        
        self.debugGenerator("getSpeechForTearOffMenuItem",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTerminal(self, obj, already_focused):
        """Get the speech for a terminal
        
        Arguments:
        - obj: the terminal
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = ""
    
        speakRolenames = settings.getSetting("speakRolenames",
                                             settings.ROLENAME_LONG)
        
        label = None
        frame = a11y.getFrame(obj)
        if frame:
            label = frame.name
        if label is None:
            label = obj.label
        text = label
            
        if not speakRolenames == settings.ROLENAME_NONE:
            text += " " + getSpeechForRoleName(obj)
    
        text += ". "
        
        self.debugGenerator("getSpeechForTerminal",
                            obj,
                            already_focused,
                            text)
            
        return text
    
    
    def getSpeechForToggleButton(self, obj, already_focused):
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
                text = self.getSpeechForLabelAndRole(obj) \
                       + _("pressed") + ". " \
                       + self.getSpeechForAccelerator(obj) \
                       + self.getSpeechForAvailability(obj)
            else:
                text = _("pressed") + ". "
        else:
            if already_focused == False:
                text = self.getSpeechForLabelAndRole(obj) \
                       + _("not pressed") + ". " \
                       + self.getSpeechForAccelerator(obj) \
                       + self.getSpeechForAvailability(obj)
            else:
                text = _("not pressed") + ". "
    
        self.debugGenerator("getSpeechForToggleButton",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForToolBar(self, obj, already_focused):
        """Get the speech for a tool bar
        
        Arguments:
        - obj: the tool bar
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForToolBar",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTree(self, obj, already_focused):
        """Get the speech for a tree
        
        Arguments:
        - obj: the tree
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForTreeTable",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForTreeTable(self, obj, already_focused):
        """Get the speech for a tree table
        
        Arguments:
        - obj: the tree table
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """

        text = self.getDefaultSpeech(obj, already_focused)
        
        self.debugGenerator("getSpeechForTreeTable",
                            obj,
                            already_focused,
                            text)
    
        return text
    
    
    def getSpeechForWindow(self, obj, already_focused):
        """Get the speech for a window
        
        Arguments:
        - obj: the window
        - already_focused: if False, the obj just received focus
    
        Returns text to be spoken for the object.
        """
        
        text = self.getDefaultSpeech(obj, already_focused)

        self.debugGenerator("getSpeechForWindow",
                            obj,
                            already_focused,
                            text)
    
        return text
