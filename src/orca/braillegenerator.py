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

"""Utilities for obtaining braille strings for objects.  In general,
there probably should be a singleton instance of the BrailleUtil
class.  For those wishing to override the braille generators, however,
one can create a new instance and replace/extend the braille
generators as they see fit."""

import math

import a11y
import braille
import core
import debug

import orca
import rolenames
import settings

from orca_i18n import _                     # for gettext support
from rolenames import getBrailleForRoleName # localized role names

class BrailleGenerator:
    """Takes accessible objects and produces a list of braille Regions
    for those objects.  See the getBrailleRegions method, which is the
    primary entry point.  Subclasses can feel free to override/extend
    the brailleGenerators instance field as they see fit."""
    
    def __init__(self):
        self.brailleGenerators = {}
        self.brailleGenerators[rolenames.ROLE_ALERT]               = \
             self._getBrailleRegionsForAlert
        self.brailleGenerators[rolenames.ROLE_ANIMATION]           = \
             self._getBrailleRegionsForAnimation
        self.brailleGenerators[rolenames.ROLE_ARROW]               = \
             self._getBrailleRegionsForArrow
        self.brailleGenerators[rolenames.ROLE_CHECK_BOX]           = \
             self._getBrailleRegionsForCheckBox
        self.brailleGenerators[rolenames.ROLE_CHECK_MENU]          = \
             self._getBrailleRegionsForCheckMenuItem
        self.brailleGenerators[rolenames.ROLE_CHECK_MENU_ITEM]     = \
             self._getBrailleRegionsForCheckMenuItem
        self.brailleGenerators[rolenames.ROLE_COLUMN_HEADER]       = \
             self._getBrailleRegionsForColumnHeader
        self.brailleGenerators[rolenames.ROLE_COMBO_BOX]           = \
             self._getBrailleRegionsForComboBox
        self.brailleGenerators[rolenames.ROLE_DESKTOP_ICON]        = \
             self._getBrailleRegionsForDesktopIcon
        self.brailleGenerators[rolenames.ROLE_DIAL]                = \
             self._getBrailleRegionsForDial
        self.brailleGenerators[rolenames.ROLE_DIALOG]              = \
             self._getBrailleRegionsForDialog
        self.brailleGenerators[rolenames.ROLE_DIRECTORY_PANE]      = \
             self._getBrailleRegionsForDirectoryPane
        self.brailleGenerators[rolenames.ROLE_FRAME]               = \
             self._getBrailleRegionsForFrame
        self.brailleGenerators[rolenames.ROLE_HTML_CONTAINER]      = \
             self._getBrailleRegionsForHtmlContainer
        self.brailleGenerators[rolenames.ROLE_ICON]                = \
             self._getBrailleRegionsForIcon
        self.brailleGenerators[rolenames.ROLE_IMAGE]               = \
             self._getBrailleRegionsForImage
        self.brailleGenerators[rolenames.ROLE_LABEL]               = \
             self._getBrailleRegionsForLabel
        self.brailleGenerators[rolenames.ROLE_LIST]                = \
             self._getBrailleRegionsForList
        self.brailleGenerators[rolenames.ROLE_MENU]                = \
             self._getBrailleRegionsForMenu
        self.brailleGenerators[rolenames.ROLE_MENU_BAR]            = \
             self._getBrailleRegionsForMenuBar
        self.brailleGenerators[rolenames.ROLE_MENU_ITEM]           = \
             self._getBrailleRegionsForMenuItem
        self.brailleGenerators[rolenames.ROLE_OPTION_PANE]         = \
             self._getBrailleRegionsForOptionPane
        self.brailleGenerators[rolenames.ROLE_PAGE_TAB]            = \
             self._getBrailleRegionsForPageTab
        self.brailleGenerators[rolenames.ROLE_PAGE_TAB_LIST]       = \
             self._getBrailleRegionsForPageTabList
        self.brailleGenerators[rolenames.ROLE_PASSWORD_TEXT]       = \
             self._getBrailleRegionsForText
        self.brailleGenerators[rolenames.ROLE_PROGRESS_BAR]        = \
             self._getBrailleRegionsForProgressBar
        self.brailleGenerators[rolenames.ROLE_PUSH_BUTTON]         = \
             self._getBrailleRegionsForPushButton
        self.brailleGenerators[rolenames.ROLE_RADIO_BUTTON]        = \
             self._getBrailleRegionsForRadioButton
        self.brailleGenerators[rolenames.ROLE_RADIO_MENU]          = \
             self._getBrailleRegionsForRadioMenuItem
        self.brailleGenerators[rolenames.ROLE_RADIO_MENU_ITEM]     = \
             self._getBrailleRegionsForRadioMenuItem
        self.brailleGenerators[rolenames.ROLE_ROW_HEADER]          = \
             self._getBrailleRegionsForRowHeader
        self.brailleGenerators[rolenames.ROLE_SCROLL_BAR]          = \
             self._getBrailleRegionsForScrollBar
        self.brailleGenerators[rolenames.ROLE_SLIDER]              = \
             self._getBrailleRegionsForSlider
        self.brailleGenerators[rolenames.ROLE_SPIN_BUTTON]         = \
             self._getBrailleRegionsForSpinButton
        self.brailleGenerators[rolenames.ROLE_SPLIT_PANE]          = \
             self._getBrailleRegionsForSplitPane
        self.brailleGenerators[rolenames.ROLE_TABLE]               = \
             self._getBrailleRegionsForTable
        self.brailleGenerators[rolenames.ROLE_TABLE_CELL]          = \
             self._getBrailleRegionsForTableCell
        self.brailleGenerators[rolenames.ROLE_TABLE_COLUMN_HEADER] = \
             self._getBrailleRegionsForTableColumnHeader
        self.brailleGenerators[rolenames.ROLE_TABLE_ROW_HEADER]    = \
             self._getBrailleRegionsForTableRowHeader
        self.brailleGenerators[rolenames.ROLE_TEAR_OFF_MENU_ITEM]  = \
             self._getBrailleRegionsForMenu
        self.brailleGenerators[rolenames.ROLE_TERMINAL]            = \
             self._getBrailleRegionsForTerminal
        self.brailleGenerators[rolenames.ROLE_TEXT]                = \
             self._getBrailleRegionsForText
        self.brailleGenerators[rolenames.ROLE_TOGGLE_BUTTON]       = \
             self._getBrailleRegionsForToggleButton
        self.brailleGenerators[rolenames.ROLE_TOOL_BAR]            = \
             self._getBrailleRegionsForToolBar
        self.brailleGenerators[rolenames.ROLE_TREE]                = \
             self._getBrailleRegionsForTable
        self.brailleGenerators[rolenames.ROLE_TREE_TABLE]          = \
             self._getBrailleRegionsForTable
        self.brailleGenerators[rolenames.ROLE_WINDOW]              = \
             self._getBrailleRegionsForWindow

        
    def _getBrailleTextForAccelerator(self, obj):
        """Returns a string to be displayed that describes the keyboard
        accelerator (and possibly shortcut) for the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a string to be displayed.
        """

        text = ""

        result = a11y.getAcceleratorAndShortcut(obj)
    
        accelerator = result[0]
        shortcut = result[1]
    
        if len(accelerator) > 0:
            text += "(" + accelerator + ")"
    
        # [[[TODO: WDW - various stuff preserved while we work out the
        # desired verbosity here.]]]
        #
        #if len(shortcut) > 0:
        #    text += "(" + shortcut + ")"
            
        return text
    
    
    def _getBrailleTextForAvailability(self, obj):
        """Returns a string to be displayed that describes the availability
        of the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a string to be displayed.
        """
        
        if obj.state.count(core.Accessibility.STATE_SENSITIVE):
            return ""
        else:
            return _("grayed")
    
    
    def _getBrailleTextForValue(self, obj):
        """Returns the text to be displayed for the object's current value.
    
        Arguments:
        - obj: the Accessible object that may or may not have a value.
    
        Returns a string representing the value.
        """
    
        value = obj.value
    
        if value is None:
            return ""
        
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
            minimumIncrement = (value.maximumValue - value.minimumValue) / 100.0
    
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
    
        # [[[TODO: WDW - probably want to do this as a percentage at some
        # point?  Logged as bugzilla bug 319743.]]]
        #
        return valueString


    def _debugGenerator(self, generatorName, obj):
        """Prints debug.LEVEL_FINER information regarding the braille
        generator.

        Arguments:
        - generatorName: the name of the generator
        - obj: the object being presented
        """

        debug.println(debug.LEVEL_FINER,
                      "GENERATOR: %s" % generatorName)
        debug.println(debug.LEVEL_FINER,
                      "           obj             = %s" % obj.name)
        debug.println(debug.LEVEL_FINER,
                      "           role            = %s" % obj.role)


    def _getDefaultBrailleRegions(self, obj):
        """Gets text to be displayed for the current object's name,
        role, and any accelerators.  This is usually the fallback
        braille generator should no other specialized braille
        generator exist for this object.

        Arguments:
        - obj: an Accessible
    
        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("_getDefaultBrailleRegions", obj)
        
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label

        value = self._getBrailleTextForValue(obj)
        if len(value) > 0:
            if len(text):
                text += " "
            text += value
        
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if len(text):
                text += " "
            text += getBrailleForRoleName(obj)

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]


    def _getBrailleRegionsForAlert(self, obj):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.
    
        Arguments:
        - obj: the Accessible dialog
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self._debugGenerator("_getBrailleRegionsForAlert", obj)
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForAnimation(self, obj):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.
    
        Arguments:
        - obj: the Accessible dialog
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self._debugGenerator("_getBrailleRegionsForAnimation", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label
        
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if len(text):
                text += " "
            text += getBrailleForRoleName(obj)
    
        if obj.description:
            if len(text):
                text += ": "
            text += obj.description
    
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForArrow(self, obj):
        """Gets text to be displayed for an arrow.
    
        Arguments:
        - obj: the arrow
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self._debugGenerator("_getBrailleRegionsForArrow", obj)
    
        # [[[TODO: determine orientation of arrow. Logged as bugzilla bug
        # 319744.]]]
        # text = arrow direction (left, right, up, down)
        #
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForCheckBox(self, obj):
        """Get the braille for a check box.  If the check box already had
        focus, then only the state is displayed.
        
        Arguments:
        - obj: the check box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForCheckBox", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label
        if len(text):
            text += " "
            
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            text += "<x>"
        else:
            text += "< >"
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            text += " " + getBrailleForRoleName(obj)

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForCheckMenuItem(self, obj):
        """Get the braille for a check menu item.  If the check menu item
        already had focus, then only the state is displayed.
        
        Arguments:
        - obj: the check menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForCheckMenuItem", obj)
        
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label
        if len(text):
            text += " "

        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            text += "<x>"
        else:
            text += "< >"
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if obj == orca.locusOfFocus:
                text += " " + getBrailleForRoleName(obj)
                availability = self._getBrailleTextForAvailability(obj)
                if len(availability) > 0:
                    text += " " + availability + " "
                accelerator = self._getBrailleTextForAccelerator(obj)
                if len(accelerator) > 0:
                    text += accelerator
    
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForColumnHeader(self, obj):
        """Get the braille for a column header.
        
        Arguments:
        - obj: the column header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForColumnHeader", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForComboBox(self, obj):
        """Get the braille for a combo box.  If the combo box already has
        focus, then only the selection is displayed.
        
        Arguments:
        - obj: the combo box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForComboBox", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        regions = []
        regions.append(braille.Region(obj.label + " "))
    
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
        childCount = obj.childCount
        i = 0
        while i < childCount:
            child = obj.child(i)
            if child.role == rolenames.ROLE_TEXT:
                textObj = child
            i = i + 1
    
        if textObj:
            regions.append(braille.Text(textObj))
        else:
            selectedItem = None
            comboSelection = obj.selection
            if comboSelection and comboSelection.nSelectedChildren > 0:
                selectedItem = a11y.makeAccessible(\
                    comboSelection.getSelectedChild(0))
            if selectedItem:
                regions.append(braille.Region(selectedItem.label))
            else:
                if obj.text:
                    regions.append(braille.Text(obj))
                else:
                    debug.println(
                        debug.LEVEL_SEVERE,
                        "ERROR: Could not find selected item for combo box.")

        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            regions.append(braille.Region(" " + getBrailleForRoleName(obj)))
                
        # [[[TODO: WDW - perhaps if a text area was created, we should
        # give focus to it.]]]
        #
        return [regions, regions[0]]
    
    
    def _getBrailleRegionsForDesktopIcon(self, obj):
        """Get the braille for a desktop icon.
        
        Arguments:
        - obj: the desktop icon
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForDesktopIcon", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForDial(self, obj):
        """Get the braille for a dial.
        
        Arguments:
        - obj: the dial
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        # [[[TODO: WDW - might need to include the value here?  Logged as
        # bugzilla bug 319746.]]]
        #
        self._debugGenerator("_getBrailleRegionsForDial", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForDialog(self, obj):
        """Get the braille for a dialog box.
        
        Arguments:
        - obj: the dialog box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForDialog", obj)
    
        return self._getBrailleRegionsForAlert(obj)
    
    
    def _getBrailleRegionsForDirectoryPane(self, obj):
        """Get the braille for a directory pane.
        
        Arguments:
        - obj: the dial
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForDirectoryPane", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForFrame(self, obj):
        """Get the braille for a frame.
        
        Arguments:
        - obj: the frame
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForFrame", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForHtmlContainer(self, obj):
        """Get the braille for an HTML container.
        
        Arguments:
        - obj: the dial
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForHtmlContainer", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForIcon(self, obj):
        """Get the braille for an icon.
        
        Arguments:
        - obj: the icon
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForIcon", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
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
            text += getBrailleForRoleName(obj)

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForImage(self, obj):
        """Get the braille for an image.
        
        Arguments:
        - obj: the image
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForImage", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForLabel(self, obj):
        """Get the braille for a label.
        
        Arguments:
        - obj: the label
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForLabel", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForList(self, obj):
        """Get the braille for a list.
        
        Arguments:
        - obj: the list
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        # [[[TODO: WDW - include how many items in the list?
        # Perhaps should also include current list item in here?
        # Logged as bugzilla bug 319749.]]]
        #
        self._debugGenerator("_getBrailleRegionsForList", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForMenu(self, obj):
        """Get the braille for a menu.
        
        Arguments:
        - obj: the menu
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForMenu", obj)

        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label
        
        if len(text):
            text += " "
        text += getBrailleForRoleName(obj)
        
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if obj == orca.locusOfFocus:
                availability = self._getBrailleTextForAvailability(obj)
                if len(availability) > 0:
                    text += " " + availability + " "
                accelerator = self._getBrailleTextForAccelerator(obj)
                if len(accelerator) > 0:
                    text += accelerator

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]

    
    def _getBrailleRegionsForMenuBar(self, obj):
        """Get the braille for a menu bar.
        
        Arguments:
        - obj: the menu bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForMenuBar", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForMenuItem(self, obj):
        """Get the braille for a menu item.
        
        Arguments:
        - obj: the menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForMenuItem", obj)

        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label
        
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if obj == orca.locusOfFocus:
                # [[[TODO - WDW comment this out for now until we work
                # out verbosity.]]]
                #
                #text += " " + getBrailleForRoleName(obj)
                availability = self._getBrailleTextForAvailability(obj)
                if len(availability) > 0:
                    text += " " + availability + " "
                accelerator = self._getBrailleTextForAccelerator(obj)
                if len(accelerator) > 0:
                    text += accelerator

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]

    
    def _getBrailleRegionsForText(self, obj):
        """Get the braille for a text component.
        
        Arguments:
        - obj: the text component
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForText", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        regions = []
    
        textRegion = braille.Text(obj, obj.label)
        regions.append(textRegion)

        eol = braille.Region(" $l")
        regions.append(eol)

        # We do not want the role at the end of text areas.
        #
        #if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
        #    text = " " + getBrailleForRoleName(obj)
        #regions.append(braille.Region(text))
        
        return [regions, textRegion]


    def _getBrailleRegionsForOptionPane(self, obj):
        """Get the braille for an option pane.
        
        Arguments:
        - obj: the option pane
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForOptionPane", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForPageTab(self, obj):
        """Get the braille for a page tab.
        
        Arguments:
        - obj: the page tab
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForPageTab", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label
        
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if obj == orca.locusOfFocus:
                text += " " + getBrailleForRoleName(obj)
                accelerator = self._getBrailleTextForAccelerator(obj)
                if len(accelerator) > 0:
                    text += accelerator

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForPageTabList(self, obj):
        """Get the braille for a page tab list.
        
        Arguments:
        - obj: the page tab list
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForPageTabList", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForProgressBar(self, obj):
        """Get the braille for a progress bar.  If the object already
        had focus, just the new value is displayed.
        
        Arguments:
        - obj: the progress bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self._debugGenerator("_getBrailleRegionsForProgressBar", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForPushButton(self, obj):
        """Get the braille for a push button
        
        Arguments:
        - obj: the push button
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForPushButton", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForRadioButton(self, obj):
        """Get the braille for a radio button.  If the button already had
        focus, then only the state is displayed.
        
        Arguments:
        - obj: the check box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForRadioButton", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        text = obj.label
        if len(text):
            text += " "
    
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            text += "&=y"
        else:
            text += "& y"
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            text += " " + getBrailleForRoleName(obj)

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForRadioMenuItem(self, obj):
        """Get the braille for a radio menu item.  If the menu item
        already had focus, then only the state is displayed.
        
        Arguments:
        - obj: the check menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForRadioMenuItem", obj)

        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        text = obj.label
        if len(text):
            text += " "

        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            text += "&=y"
        else:
            text += "& y"
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if obj == orca.locusOfFocus:
                text += " " + getBrailleForRoleName(obj)
                availability = self._getBrailleTextForAvailability(obj)
                if len(availability) > 0:
                    text += " " + availability + " "
                accelerator = self._getBrailleTextForAccelerator(obj)
                if len(accelerator) > 0:
                    text += accelerator

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForRowHeader(self, obj):
        """Get the braille for a row header.
        
        Arguments:
        - obj: the column header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForRowHeader", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForScrollBar(self, obj):
        """Get the braille for a scroll bar.
        
        Arguments:
        - obj: the scroll bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        # [[[TODO: WDW - want to get orientation.  Logged as bugzilla bug
        # 319744.]]]
        #
        self._debugGenerator("_getBrailleRegionsForScrollBar", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForSlider(self, obj):
        """Get the braille for a slider.  If the object already
        had focus, just the value is displayed.
        
        Arguments:
        - obj: the slider
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForProgressBar", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForSpinButton(self, obj):
        """Get the braille for a spin button.  If the object already has
        focus, then only the new value is displayed.
        
        Arguments:
        - obj: the spin button
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self._debugGenerator("_getBrailleRegionsForSpinButton", obj)
    
        return self._getBrailleRegionsForText(obj)
    
    
    def _getBrailleRegionsForSplitPane(self, obj):
        """Get the braille for a split pane.
        
        Arguments:
        - obj: the split pane
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForSplitPane", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForTable(self, obj):
        """Get the braille for a table
        
        Arguments:
        - obj: the table
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTable", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a table cell
        
        Arguments:
        - obj: the table
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTableCell", obj)

        regions = []
        
        # [[[TODO: WDW - Attempt to infer the cell type.  There's a
        # bunch of stuff we can do here, such as check the EXPANDABLE
        # state, check the NODE_CHILD_OF relation, etc.  Logged as
        # bugzilla bug 319750.]]]
        #
        action = obj.action
        if action:
            i = 0
            while i < action.nActions:
                if action.getName(i) == "toggle":
                    obj.role = rolenames.ROLE_CHECK_BOX
                    regions = self._getBrailleRegionsForCheckBox(obj)
                    obj.role = rolenames.ROLE_TABLE_CELL
                    break
                #elif action.getName(i) == "edit":
                #    text = self._getSpeechForText(obj, True)
                #    break
                i += 1

        if len(regions) == 0:
            regions = self._getDefaultBrailleRegions(obj)
            
        # [[[TODO: WDW - HACK attempt to determine if this is a node;
        # if so, describe its state.]]]
        #
        if obj.state.count(core.Accessibility.STATE_EXPANDABLE):
            if obj.state.count(core.Accessibility.STATE_EXPANDED):            
                regions[0].append(braille.Region(" " + _("expanded")))
            else:
                regions[0].append(braille.Region(" " + _("collapsed")))

        level = a11y.getNodeLevel(obj)
        if level >= 0:
            regions[0].append(braille.Region(" " + _("TREE LEVEL %d") \
                                             % (level + 1)))
            
        return regions
    
    
    def _getBrailleRegionsForTableColumnHeader(self, obj):
        """Get the braille for a table column header
        
        Arguments:
        - obj: the table column header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTableColumnHeader", obj)
    
        return self._getBrailleRegionsForColumnHeader(obj)
    
    
    def _getBrailleRegionsForTableRowHeader(self, obj):
        """Get the braille for a table row header
        
        Arguments:
        - obj: the table row header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTableRowHeader", obj)
    
        return self._getBrailleRegionsForRowHeader(obj)
    
    
    def _getBrailleRegionsForTearOffMenuItem(self, obj):
        """Get the braille for a tear off menu item
        
        Arguments:
        - obj: the tear off menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTearOffMenuItem", obj)
    
        text = getBrailleForRoleName(obj)
    
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def _getBrailleRegionsForTerminal(self, obj):
        """Get the braille for a terminal
        
        Arguments:
        - obj: the terminal
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTerminal", obj)
    
        verbosity = settings.getSetting("brailleVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        label = None
        frame = a11y.getFrame(obj)
        if frame:
            label = frame.name
        if label is None:
            label = obj.label
        text = label
            
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            if len(text):
                text += " "
            text += getBrailleForRoleName(obj)
    
        regions = []
        regions.append(braille.Region(text))
    
        textRegion = braille.Text(obj)
        regions.append(textRegion)

        return [regions, textRegion]


    def _getBrailleRegionsForToggleButton(self, obj):
        """Get the braille for a toggle button.  If the toggle button already
        had focus, then only the state is displayed.
        
        Arguments:
        - obj: the check box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForToggleButton", obj)
    
        return self._getBrailleRegionsForRadioButton(obj)
    
    
    def _getBrailleRegionsForToolBar(self, obj):
        """Get the braille for a tool bar
        
        Arguments:
        - obj: the tool bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForToolBar", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForTree(self, obj):
        """Get the braille for a tree
        
        Arguments:
        - obj: the tree
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTreeTable", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForTreeTable(self, obj):
        """Get the braille for a tree table
        
        Arguments:
        - obj: the tree table
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForTreeTable", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def _getBrailleRegionsForWindow(self, obj):
        """Get the braille for a window
        
        Arguments:
        - obj: the window
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self._debugGenerator("_getBrailleRegionsForWindow", obj)
    
        return self._getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegions(self, obj, groupChildren=True):
        """Get the braille regions for an Accessible object.  This
        will look first to the specific braille generators and then to
        the default braille generator.  This method is the primary
        method that external callers of this class should use.
    
        Arguments:
        - obj: the object
        - groupChildren: if True, children of an object should be displayed
                         together with their parent, where each child is
                         separated by _ and the selected child is the Region
                         that should get focus.
                          
        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.  """

        # If we want to group the children, first see if obj is a child of
        # something we like to group.  If so, then reset the obj to the obj's
        # parent.  If not, see if the obj is the container of things we like
        # to group.  If all fails, we don't try grouping.
        #
        reallyGroupChildren = False
        if groupChildren:
            parent = obj.parent
            isChild = parent \
                      and ((parent.role == rolenames.ROLE_MENU) \
                           or (parent.role == rolenames.ROLE_MENU_BAR) \
                           or (parent.role == rolenames.ROLE_PAGE_TAB_LIST))
            if isChild:
                obj = parent
                reallyGroupChildren = True
            else:
                reallyGroupChildren = \
                    (obj.role == rolenames.ROLE_MENU) \
                    or (obj.role == rolenames.ROLE_MENU_BAR) \
                    or (obj.role == rolenames.ROLE_PAGE_TAB_LIST)
            
        if self.brailleGenerators.has_key(obj.role):
            generator = self.brailleGenerators[obj.role]
        else:
            generator = self._getDefaultBrailleRegions

        result = generator(obj)
        regions = result[0]
        selectedRegion = result[1]
        
        if reallyGroupChildren:
            regions.append(braille.Region(" "))
            selection = obj.selection
            childCount = obj.childCount
            i = 0
            while i < childCount:
                child = obj.child(i)

                if child.role != rolenames.ROLE_SEPARATOR:
                # the following line has been removed because insensitive
                # menu items can get focus in StarOffice.
                #
                # and child.state.count(core.Accessibility.STATE_SENSITIVE):

                    if (i > 0) and (i < (self, childCount - 1)):
                        regions.append(braille.Region(" _ "))
    
                    result = self.getBrailleRegions(child, False)
                    regions.extend(result[0])
    
                    if selection and selection.isChildSelected(i):
                        selectedRegion = result[1]
                    
                i = i + 1
            
        return [regions, selectedRegion]


    def getBrailleContext(self, obj):
        """Get the braille regions that describe the context (i.e.,
        names/roles of the container hierarchy) of the object.
    
        Arguments:
        - obj: the object
                          
        Returns a list of Regions to display.
        """

        verbosity = settings.getSetting(
            "brailleVerbosityLevel",
            settings.VERBOSITY_LEVEL_VERBOSE)

        brailleRolenameStyle = settings.getSetting(
            "brailleRolenameStyle",
            settings.BRAILLE_ROLENAME_STYLE_LONG)

        regions = []
        parent = obj.parent
        if parent \
           and ((parent.role == rolenames.ROLE_MENU) \
                or (parent.role == rolenames.ROLE_MENU_BAR) \
                or (parent.role == rolenames.ROLE_PAGE_TAB_LIST)):
            parent = parent.parent        
        while parent and (parent.parent != parent):
            # [[[TODO: WDW - we might want to include more things here
            # besides just those things that have labels.  For example,
            # page tab lists might be a nice thing to include. Logged
            # as bugzilla bug 319751.]]]
            #
            if (parent.role != rolenames.ROLE_FILLER) \
                and (parent.role != rolenames.ROLE_SPLIT_PANE):
                if (len(parent.label) > 0) \
                    or (parent.role != rolenames.ROLE_PANEL):
                    regions.append(braille.Region(" "))
                    result = self.getBrailleRegions(parent, False)
                    regions.extend(result[0])
                    
            parent = parent.parent

        regions.reverse()

        # Now, we'll treat table row and column headers as context as
        # well.  This requires special handling because we're making
        # headers seem hierarchical in the context, but they are not
        # hierarchical in the containment hierarchicy.  If both exist,
        # we first show the row header then the column header.
        #
        parent = obj.parent
        if parent and parent.table:
            row = parent.table.getRowAtIndex(obj.index)
            desc = parent.table.getRowDescription(row)
            if desc and len(desc):
                if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                    if brailleRolenameStyle \
                           == settings.BRAILLE_ROLENAME_STYLE_LONG:
                        text = desc + " " + rolenames.rolenames[\
                            rolenames.ROLE_ROW_HEADER].brailleLong
                    else:
                        text = desc + " " + rolenames.rolenames[\
                            rolenames.ROLE_ROW_HEADER].brailleShort
                else:
                    text = desc
                regions.append(braille.Region(text))

            col = parent.table.getColumnAtIndex(obj.index)
            desc = parent.table.getColumnDescription(col)
            if desc and len(desc):
                if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                    if brailleRolenameStyle \
                           == settings.BRAILLE_ROLENAME_STYLE_LONG:
                        text = desc + " " + rolenames.rolenames[\
                            rolenames.ROLE_COLUMN_HEADER].brailleLong
                    else:
                        text = desc + " " + rolenames.rolenames[\
                            rolenames.ROLE_COLUMN_HEADER].brailleShort
                else:
                    text = desc
                regions.append(braille.Region(text))
        
        return regions
