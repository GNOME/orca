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

from orca_i18n import _                          # for gettext support
from rolenames import getShortBrailleForRoleName # localized role names
from rolenames import getLongBrailleForRoleName  # localized role names

class BrailleGenerator:
    """Takes accessible objects and produces a list of braille Regions
    for those objects.  See the getBrailleRegions method, which is the
    primary entry point.  Subclasses can feel free to override/extend
    the brailleGenerators instance field as they see fit."""
    
    def __init__(self, region=None):
        self.brailleGenerators = {}
        self.brailleGenerators["alert"]               = \
             self.getBrailleRegionsForAlert
        self.brailleGenerators["animation"]           = \
             self.getBrailleRegionsForAnimation
        self.brailleGenerators["arrow"]               = \
             self.getBrailleRegionsForArrow
        self.brailleGenerators["check box"]           = \
             self.getBrailleRegionsForCheckBox
        self.brailleGenerators["check menu item"]     = \
             self.getBrailleRegionsForCheckMenuItem
        self.brailleGenerators["column_header"]       = \
             self.getBrailleRegionsForColumnHeader
        self.brailleGenerators["combo box"]           = \
             self.getBrailleRegionsForComboBox
        self.brailleGenerators["desktop icon"]        = \
             self.getBrailleRegionsForDesktopIcon
        self.brailleGenerators["dial"]                = \
             self.getBrailleRegionsForDial
        self.brailleGenerators["dialog"]              = \
             self.getBrailleRegionsForDialog
        self.brailleGenerators["directory pane"]      = \
             self.getBrailleRegionsForDirectoryPane
        self.brailleGenerators["frame"]               = \
             self.getBrailleRegionsForFrame
        self.brailleGenerators["html container"]      = \
             self.getBrailleRegionsForHtmlContainer
        self.brailleGenerators["icon"]                = \
             self.getBrailleRegionsForIcon
        self.brailleGenerators["image"]               = \
             self.getBrailleRegionsForImage
        self.brailleGenerators["label"]               = \
             self.getBrailleRegionsForLabel
        self.brailleGenerators["list"]                = \
             self.getBrailleRegionsForList
        self.brailleGenerators["menu"]                = \
             self.getBrailleRegionsForMenu
        self.brailleGenerators["menu bar"]            = \
             self.getBrailleRegionsForMenuBar
        self.brailleGenerators["menu item"]           = \
             self.getBrailleRegionsForMenuItem
        self.brailleGenerators["multi line text"]     = \
             self.getBrailleRegionsForText
        self.brailleGenerators["option pane"]         = \
             self.getBrailleRegionsForOptionPane
        self.brailleGenerators["page tab"]            = \
             self.getBrailleRegionsForPageTab
        self.brailleGenerators["page tab list"]       = \
             self.getBrailleRegionsForPageTabList
        self.brailleGenerators["password text"]       = \
             self.getBrailleRegionsForText
        self.brailleGenerators["progress bar"]        = \
             self.getBrailleRegionsForProgressBar
        self.brailleGenerators["push button"]         = \
             self.getBrailleRegionsForPushButton
        self.brailleGenerators["radio button"]        = \
             self.getBrailleRegionsForRadioButton
        self.brailleGenerators["radio menu item"]     = \
             self.getBrailleRegionsForRadioMenuItem
        self.brailleGenerators["row_header"]          = \
             self.getBrailleRegionsForRowHeader
        self.brailleGenerators["scroll bar"]          = \
             self.getBrailleRegionsForScrollBar
        self.brailleGenerators["single line text"]    = \
             self.getBrailleRegionsForText
        self.brailleGenerators["slider"]              = \
             self.getBrailleRegionsForSlider
        self.brailleGenerators["spin button"]         = \
             self.getBrailleRegionsForSpinButton
        self.brailleGenerators["split pane"]          = \
             self.getBrailleRegionsForSplitPane
        self.brailleGenerators["table"]               = \
             self.getBrailleRegionsForTable
        self.brailleGenerators["table cell"]          = \
             self.getBrailleRegionsForTableCell
        self.brailleGenerators["table column header"] = \
             self.getBrailleRegionsForTableColumnHeader
        self.brailleGenerators["table row header"]    = \
             self.getBrailleRegionsForTableRowHeader
        self.brailleGenerators["tear off menu item"]  = \
             self.getBrailleRegionsForMenu
        self.brailleGenerators["terminal"]            = \
             self.getBrailleRegionsForTerminal
        self.brailleGenerators["text"]                = \
             self.getBrailleRegionsForText
        self.brailleGenerators["toggle button"]       = \
             self.getBrailleRegionsForToggleButton
        self.brailleGenerators["tool bar"]            = \
             self.getBrailleRegionsForToolBar
        self.brailleGenerators["tree"]                = \
             self.getBrailleRegionsForTable
        self.brailleGenerators["tree table"]          = \
             self.getBrailleRegionsForTable
        self.brailleGenerators["window"]              = \
             self.getBrailleRegionsForWindow

        
    def getBrailleTextForAccelerator(self, obj):
        """Returns a string to be displayed that describes the keyboard
        accelerator (and possibly shortcut) for the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a string to be displayed.
        """
    
        brailleAccelerators = settings.getSetting("brailleAccelerators",
                                                  settings.ACCELERATOR_SHORT)
    
        text = ""
        if not brailleAccelerators == settings.ACCELERATOR_NONE:
            return text
        
        result = a11y.getAcceleratorAndShortcut(obj)
    
        accelerator = result[0]
        shortcut = result[1]
    
        # settings.ACCELERATOR_SHORT just shows the accelerator
        #
        if len(accelerator) > 0:
            text += "(" + accelerator + ")"
    
        # settings.ACCELERATOR_LONG adds in the shortcut.
        #
        if (brailleAccelerators == settings.ACCELERATOR_LONG) \
            and (len(shortcut) > 0):
            text += "(" + shortcut + ")"
            
        return text
    
    
    def getBrailleTextForAvailability(self, obj):
        """Returns a string to be displayed that describes the availability
        of the given object.
    
        Arguments:
        - obj: the Accessible object
    
        Returns a string to be displayed.
        """
        
        if obj.state.count(core.Accessibility.STATE_SENSITIVE):
            return ""
        else:
            return _("unavailable")
    
    
    def getBrailleTextForValue(self, obj):
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
        # point?]]]
        #
        return valueString

    def getBrailleContext(self, obj):
        """Get the braille regions that describe the context (i.e.,
        names/roles of the container hierarchy) of the object.
    
        Arguments:
        - obj: the object
                          
        Returns a list of Regions to display.
        """

        # We want to follow the same grouping logic in getBrailleRegions.
        # 
        parent = obj.parent
        if parent \
           and ((parent.role == rolenames.ROLE_MENU) \
                or (parent.role == rolenames.ROLE_MENU_BAR) \
                or (parent.role == rolenames.ROLE_PAGE_TAB_LIST)):
            obj = parent

        regions = []
        while parent:
            if len(parent.label) > 0:
                regions.append(braille.Region(" "))
                result = self.getBrailleRegions(parent, False)
                regions.extend(result[0])
            parent = parent.parent

        regions.reverse()

        return regions
    
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
            generator = self.getDefaultBrailleRegions

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
                if child.role != rolenames.ROLE_SEPARATOR \
                    and child.state.count(core.Accessibility.STATE_SENSITIVE):

                    if (i > 0) and (i < (self, childCount - 1)):
                        regions.append(braille.Region(" _ "))
    
                    result = self.getBrailleRegions(child, False)
                    regions.extend(result[0])
    
                    if selection and selection.isChildSelected(i):
                        selectedRegion = result[1]
                    
                i = i + 1
            
        return [regions, selectedRegion]


    def debugGenerator(self, generatorName, obj):
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


    def getDefaultBrailleRegions(self, obj):
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

        self.debugGenerator("getDefaultBrailleRegions", obj)
        
        brailleRolenames = settings.getSetting("brailleRolenames",
                                               settings.ROLENAME_LONG)

        text = obj.label
        
        value = self.getBrailleTextForValue(obj)
        if len(value) > 0:
            text += " " + value
        
        if brailleRolenames == settings.ROLENAME_SHORT:
            text += " " + getShortBrailleForRoleName(obj)
        elif brailleRolenames == settings.ROLENAME_LONG:
            text += " " + getLongBrailleForRoleName(obj)

        accelerator = self.getBrailleTextForAccelerator(obj)
        if len(accelerator) > 0:
            text += " " + accelerator
        
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]


    def getBrailleRegionsForAlert(self, obj):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.
    
        Arguments:
        - obj: the Accessible dialog
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self.debugGenerator("getBrailleRegionsForAlert", obj)
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForAnimation(self, obj):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.
    
        Arguments:
        - obj: the Accessible dialog
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self.debugGenerator("getBrailleRegionsForAnimation", obj)
    
        brailleRolenames = settings.getSetting("brailleRolenames",
                                               settings.ROLENAME_LONG)
    
        text = obj.label
        
        if brailleRolenames == settings.ROLENAME_SHORT:
            text += " " + getShortBrailleForRoleName(obj)
        elif brailleRolenames == settings.ROLENAME_LONG:
            text += " " + getLongBrailleForRoleName(obj)
    
        if obj.description:
            text += " " + obj.description
    
        accelerator = self.getBrailleTextForAccelerator(obj)
        if len(accelerator) > 0:
            text += " " + accelerator
    
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def getBrailleRegionsForArrow(self, obj):
        """Gets text to be displayed for an arrow.
    
        Arguments:
        - obj: the arrow
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self.debugGenerator("getBrailleRegionsForArrow", obj)
    
        # [[[TODO: determine orientation of arrow.]]]
        # text = arrow direction (left, right, up, down)
        #
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForCheckBox(self, obj):
        """Get the braille for a check box.  If the check box already had
        focus, then only the state is displayed.
        
        Arguments:
        - obj: the check box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForCheckBox", obj)
    
        brailleRolenames = settings.getSetting("brailleRolenames",
                                               settings.ROLENAME_LONG)
    
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            text = obj.label + " <x>"
        else:
            text = obj.label + " < >"
            
        if brailleRolenames == settings.ROLENAME_SHORT:
            text += " " + getShortBrailleForRoleName(obj)
        elif brailleRolenames == settings.ROLENAME_LONG:
            text += " " + getLongBrailleForRoleName(obj)
    
        accelerator = self.getBrailleTextForAccelerator(obj)
        if len(accelerator) > 0:
            text += " " + accelerator
    
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def getBrailleRegionsForCheckMenuItem(self, obj):
        """Get the braille for a check menu item.  If the check menu item
        already had focus, then only the state is displayed.
        
        Arguments:
        - obj: the check menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForCheckMenuItem", obj)
    
        # [[[TODO: WDW - only show accelerator when the menu item is
        # selected.]]]
        #
        return self.getBrailleRegionsForCheckBox(obj)
    
    
    def getBrailleRegionsForColumnHeader(self, obj):
        """Get the braille for a column header.
        
        Arguments:
        - obj: the column header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForColumnHeader", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForComboBox(self, obj):
        """Get the braille for a combo box.  If the combo box already has
        focus, then only the selection is displayed.
        
        Arguments:
        - obj: the combo box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForComboBox", obj)
    
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
    
        # [[[TODO: WDW - perhaps if a text area was created, we should
        # give focus to it.]]]
        #
        return [regions, regions[0]]
    
    
    def getBrailleRegionsForDesktopIcon(self, obj):
        """Get the braille for a desktop icon.
        
        Arguments:
        - obj: the desktop icon
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForDesktopIcon", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForDial(self, obj):
        """Get the braille for a dial.
        
        Arguments:
        - obj: the dial
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        # [[[TODO: WDW - might need to include the value here?]]]
        #
        self.debugGenerator("getBrailleRegionsForDial", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForDialog(self, obj):
        """Get the braille for a dialog box.
        
        Arguments:
        - obj: the dialog box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForDialog", obj)
    
        return self.getBrailleRegionsForAlert(obj)
    
    
    def getBrailleRegionsForDirectoryPane(self, obj):
        """Get the braille for a directory pane.
        
        Arguments:
        - obj: the dial
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForDirectoryPane", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForFrame(self, obj):
        """Get the braille for a frame.
        
        Arguments:
        - obj: the frame
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForFrame", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForHtmlContainer(self, obj):
        """Get the braille for an HTML container.
        
        Arguments:
        - obj: the dial
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForHtmlContainer", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForIcon(self, obj):
        """Get the braille for an icon.
        
        Arguments:
        - obj: the icon
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForIcon", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForImage(self, obj):
        """Get the braille for an image.
        
        Arguments:
        - obj: the image
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForImage", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForLabel(self, obj):
        """Get the braille for a label.
        
        Arguments:
        - obj: the label
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForLabel", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForList(self, obj):
        """Get the braille for a list.
        
        Arguments:
        - obj: the list
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        # [[[TODO: WDW - include how many items in the list?]]]
        # Perhaps should also include current list item in here?
        #
        self.debugGenerator("getBrailleRegionsForList", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForMenu(self, obj):
        """Get the braille for a menu.
        
        Arguments:
        - obj: the menu
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForMenu", obj)

        return self.getDefaultBrailleRegions(obj)

    
    def getBrailleRegionsForMenuBar(self, obj):
        """Get the braille for a menu bar.
        
        Arguments:
        - obj: the menu bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForMenuBar", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForMenuItem(self, obj):
        """Get the braille for a menu item.
        
        Arguments:
        - obj: the menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForMenuItem", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForText(self, obj):
        """Get the braille for a text component.
        
        Arguments:
        - obj: the text component
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForText", obj)
    
        brailleRolenames = settings.getSetting("brailleRolenames",
                                               settings.ROLENAME_LONG)
    
        regions = []
    
        regions.append(braille.Region(obj.label + " "))
        textRegion = braille.Text(obj)
        regions.append(textRegion)
        
        if brailleRolenames == settings.ROLENAME_SHORT:
            text = " " + getShortBrailleForRoleName(obj)
        else:
            text = " " + getLongBrailleForRoleName(obj)
    
        regions.append(braille.Region(text))
        
        return [regions, textRegion]
        #return [regions, regions[0]]
    
    
    def getBrailleRegionsForOptionPane(self, obj):
        """Get the braille for an option pane.
        
        Arguments:
        - obj: the option pane
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForOptionPane", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForPageTab(self, obj):
        """Get the braille for a page tab.
        
        Arguments:
        - obj: the page tab
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForPageTab", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForPageTabList(self, obj):
        """Get the braille for a page tab list.
        
        Arguments:
        - obj: the page tab list
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForPageTabList", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForProgressBar(self, obj):
        """Get the braille for a progress bar.  If the object already
        had focus, just the new value is displayed.
        
        Arguments:
        - obj: the progress bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self.debugGenerator("getBrailleRegionsForProgressBar", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForPushButton(self, obj):
        """Get the braille for a push button
        
        Arguments:
        - obj: the push button
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForPushButton", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForRadioButton(self, obj):
        """Get the braille for a radio button.  If the button already had
        focus, then only the state is displayed.
        
        Arguments:
        - obj: the check box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForRadioButton", obj)
    
        brailleRolenames = settings.getSetting("brailleRolenames",
                                               settings.ROLENAME_LONG)
    
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            text = obj.label + " &=y"
        else:
            text = obj.label + " & y"
            
        if brailleRolenames == settings.ROLENAME_SHORT:
            text += " " + getShortBrailleForRoleName(obj)
        elif brailleRolenames == settings.ROLENAME_LONG:
            text += " " + getLongBrailleForRoleName(obj)
    
        accelerator = self.getBrailleTextForAccelerator(obj)
        if len(accelerator) > 0:
            text += " " + accelerator
    
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def getBrailleRegionsForRadioMenuItem(self, obj):
        """Get the braille for a radio menu item.  If the menu item
        already had focus, then only the state is displayed.
        
        Arguments:
        - obj: the check menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForRadioMenuItem", obj)
    
        # [[[TODO: WDW - only show accelerator when the menu item is
        # selected.]]]
        #
        return self.getBrailleRegionsForRadioButton(obj)
    
    
    def getBrailleRegionsForRowHeader(self, obj):
        """Get the braille for a row header.
        
        Arguments:
        - obj: the column header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForRowHeader", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForScrollBar(self, obj):
        """Get the braille for a scroll bar.
        
        Arguments:
        - obj: the scroll bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        # [[[TODO: WDW - want to get orientation.]]]
        #
        self.debugGenerator("getBrailleRegionsForScrollBar", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForSlider(self, obj):
        """Get the braille for a slider.  If the object already
        had focus, just the value is displayed.
        
        Arguments:
        - obj: the slider
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForProgressBar", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForSpinButton(self, obj):
        """Get the braille for a spin button.  If the object already has
        focus, then only the new value is displayed.
        
        Arguments:
        - obj: the spin button
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
    
        self.debugGenerator("getBrailleRegionsForSpinButton", obj)
    
        return self.getBrailleRegionsForText(obj)
    
    
    def getBrailleRegionsForSplitPane(self, obj):
        """Get the braille for a split pane.
        
        Arguments:
        - obj: the split pane
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForSplitPane", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForTable(self, obj):
        """Get the braille for a table
        
        Arguments:
        - obj: the table
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTable", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a table cell
        
        Arguments:
        - obj: the table
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTableCell", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForTableColumnHeader(self, obj):
        """Get the braille for a table column header
        
        Arguments:
        - obj: the table column header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTableColumnHeader", obj)
    
        return self.getBrailleRegionsForColumnHeader(obj)
    
    
    def getBrailleRegionsForTableRowHeader(self, obj):
        """Get the braille for a table row header
        
        Arguments:
        - obj: the table row header
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTableRowHeader", obj)
    
        return self.getBrailleRegionsForRowHeader(obj)
    
    
    def getBrailleRegionsForTearOffMenuItem(self, obj):
        """Get the braille for a tear off menu item
        
        Arguments:
        - obj: the tear off menu item
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTearOffMenuItem", obj)
    
        brailleRolenames = settings.getSetting("brailleRolenames",
                                               settings.ROLENAME_LONG)
    
        if brailleRolenames == settings.ROLENAME_SHORT:
            text = getShortBrailleForRoleName(obj)
        elif brailleRolenames == settings.ROLENAME_LONG:
            text = getLongBrailleForRoleName(obj)
    
        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)
    
        return [regions, componentRegion]
    
    
    def getBrailleRegionsForTerminal(self, obj):
        """Get the braille for a terminal
        
        Arguments:
        - obj: the terminal
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTerminal", obj)
    
        brailleRolenames = settings.getSetting("brailleRolenames",
                                               settings.ROLENAME_LONG)
        
        text = ""
    
        label = None
        frame = a11y.getFrame(obj)
        if frame:
            label = frame.name
        if label is None:
            label = obj.label
        text = label
            
        if brailleRolenames == settings.ROLENAME_SHORT:
            text = getShortBrailleForRoleName(obj)
        elif brailleRolenames == settings.ROLENAME_LONG:
            text = getLongBrailleForRoleName(obj)
    
        regions = []
        regions.append(braille.Region(text))
    
        textRegion = braille.Text(obj)
        regions.append(textRegion)

        return [regions, textRegion]


    def getBrailleRegionsForToggleButton(self, obj):
        """Get the braille for a toggle button.  If the toggle button already
        had focus, then only the state is displayed.
        
        Arguments:
        - obj: the check box
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForToggleButton", obj)
    
        return self.getBrailleRegionsForRadioButton(obj)
    
    
    def getBrailleRegionsForToolBar(self, obj):
        """Get the braille for a tool bar
        
        Arguments:
        - obj: the tool bar
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForToolBar", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForTree(self, obj):
        """Get the braille for a tree
        
        Arguments:
        - obj: the tree
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTreeTable", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForTreeTable(self, obj):
        """Get the braille for a tree table
        
        Arguments:
        - obj: the tree table
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForTreeTable", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
    
    def getBrailleRegionsForWindow(self, obj):
        """Get the braille for a window
        
        Arguments:
        - obj: the window
    
        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """
        
        self.debugGenerator("getBrailleRegionsForWindow", obj)
    
        return self.getDefaultBrailleRegions(obj)
    
