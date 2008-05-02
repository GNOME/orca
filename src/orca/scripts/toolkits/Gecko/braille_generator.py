# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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


"""Custom script for Gecko toolkit.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.braille as braille
import orca.braillegenerator as braillegenerator
import orca.rolenames as rolenames
import orca.settings as settings

########################################################################
#                                                                      #
# Custom BrailleGenerator                                              #
#                                                                      #
########################################################################

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Provides a braille generator specific to Gecko.
    """

    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)
        self.brailleGenerators[pyatspi.ROLE_AUTOCOMPLETE] = \
             self._getBrailleRegionsForAutocomplete
        self.brailleGenerators[pyatspi.ROLE_ENTRY]        = \
             self._getBrailleRegionsForText
        self.brailleGenerators[pyatspi.ROLE_LINK]         = \
             self._getBrailleRegionsForLink

    def _getTextForRole(self, obj, role=None):
        if settings.brailleVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
           and not obj.getRole() in [pyatspi.ROLE_SECTION,
                                     pyatspi.ROLE_FORM,
                                     pyatspi.ROLE_UNKNOWN]:
            return rolenames.getBrailleForRoleName(obj, role)
        else:
            return None

    def _getBrailleRegionsForAutocomplete(self, obj):
        """Gets the braille for an autocomplete box.  We let the
        handlers for the children do the rest.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForAutocomplete", obj)

        # [[[TODO: WDW - we're doing very little here.  The goal for
        # autocomplete boxes at the moment is that their children (e.g.,
        # a text area, a menu, etc., do all the interactive work and
        # the autocomplete acts as more of a container.]]]
        #
        regions = []
        if settings.brailleVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            regions.append(braille.Region(
                rolenames.getBrailleForRoleName(obj)))
        else:
            regions.append(braille.Region(""))

        return (regions, regions[0])

    def _getBrailleRegionsForCheckBox(self, obj):
        """Get the braille for a check box.  If the check box already had
        focus, then only the state is displayed.

        Arguments:
        - obj: the check box

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForCheckBox", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                       _getBrailleRegionsForCheckBox(self, obj)
        
        # In document content (I'm not sure about XUL widgets yet), a
        # checkbox is its own little beast with no text.  So...  if it
        # is in document content and has a label, we're likely to be
        # displaying that label already.  If it doesn't have a label,
        # though, we'll display its name.
        #
        text = ""
        if not self._script.inDocumentContent():
            text = self._script.appendString(
                text, self._script.getDisplayedLabel(obj))
            text = self._script.appendString(
                text, self._script.getDisplayedText(obj))
        else:
            isLabelled = False
            relationSet = obj.getRelationSet()
            if relationSet:
                for relation in relationSet:
                    if relation.getRelationType() \
                        == pyatspi.RELATION_LABELLED_BY:
                        isLabelled = True
                        break
            if not isLabelled and obj.name and len(obj.name):
                text = self._script.appendString(text, obj.name)

        text = self._script.appendString(text, self._getTextForRole(obj))

        # get the Braille indicator
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            indicatorIndex = 2
        elif state.contains(pyatspi.STATE_CHECKED):
            indicatorIndex = 1
        else:
            indicatorIndex = 0

        regions = []

        componentRegion = braille.Component(
            obj, text,
            indicator=settings.brailleCheckBoxIndicators[indicatorIndex])
        regions.append(componentRegion)

        return [regions, componentRegion]

    def _getBrailleRegionsForRadioButton(self, obj):
        """Get the braille for a radio button.  If the radio button already
        had focus, then only the state is displayed.

        Arguments:
        - obj: the radio button

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForRadioButton", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                       _getBrailleRegionsForRadioButton(self, obj)
        
        # In document content (I'm not sure about XUL widgets yet), a
        # radio button is its own little beast with no text.  So...  if it
        # is in document content and has a label, we're likely to be
        # displaying that label already.  If it doesn't have a label,
        # though, we'll display its name.
        #
        text = ""
        if not self._script.inDocumentContent():
            text = self._script.appendString(
                text, self._script.getDisplayedLabel(obj))
            text = self._script.appendString(
                text, self._script.getDisplayedText(obj))
        else:
            isLabelled = False
            relationSet = obj.getRelationSet()
            if relationSet:
                for relation in relationSet:
                    if relation.getRelationType() \
                        == pyatspi.RELATION_LABELLED_BY:
                        isLabelled = True
                        break

            if not isLabelled and obj.name and len(obj.name):
                text = self._script.appendString(text, obj.name)

        text = self._script.appendString(text, self._getTextForRole(obj))

        indicatorIndex = int(obj.getState().contains(pyatspi.STATE_CHECKED))

        regions = []
        componentRegion = braille.Component(
            obj, text,
            indicator=settings.brailleRadioButtonIndicators[indicatorIndex])
        regions.append(componentRegion)

        return [regions, componentRegion]

    def _getBrailleRegionsForText(self, obj):
        """Gets text to be displayed for the entry of an autocomplete box.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForText", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                       _getBrailleRegionsForText(self, obj)
        
        parent = obj.parent
        if parent.getRole() != pyatspi.ROLE_AUTOCOMPLETE:
            return braillegenerator.BrailleGenerator._getBrailleRegionsForText(
                self, obj)

        regions = []

        # This is the main difference between this class and the default
        # class - we'll give this thing a name here, and we'll make it
        # be the name of the autocomplete.
        #
        label = self._script.getDisplayedLabel(parent)
        if not label or not len(label):
            label = parent.name

        textRegion = braille.Text(obj, label, " $l")
        regions.append(textRegion)
        return [regions, textRegion]

    def _getBrailleRegionsForComboBox(self, obj):
        """Get the braille for a combo box.  If the combo box already has
        focus, then only the selection is displayed.

        Arguments:
        - obj: the combo box

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForComboBox", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                     _getBrailleRegionsForComboBox(self, obj)
        
        regions = []

        label = self._script.getDisplayedLabel(obj)
        if not label and not self._script.inDocumentContent():
            label = obj.name

        focusedRegionIndex = 0
        if label and len(label):
            regions.append(braille.Region(label + " "))
            focusedRegionIndex = 1

        # With Gecko, a combo box has a menu as a child.  The text being
        # displayed for the combo box can be obtained via the selected
        # menu item.
        #
        menu = None
        for child in obj:
            if child.getRole() == pyatspi.ROLE_MENU:
                menu = child
                break
        if menu:
            child = None
            try:
                # This should work...
                #
                child = menu.querySelection().getSelectedChild(0)
            except:
                # But just in case, we'll fall back on this.
                # [[[TODO - JD: Will we ever have a case where the first
                # fails, but this will succeed???]]]
                #
                for item in menu:
                    if item.getState().contains(pyatspi.STATE_SELECTED):
                        child = item
                        break
            if child:
                regions.append(braille.Region(child.name))

        if settings.brailleVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            regions.append(braille.Region(
                " " + rolenames.getBrailleForRoleName(obj)))

        # Things may not have gone as expected above, so we'll do some
        # defensive programming to make sure we don't get an index out
        # of bounds.
        #
        if focusedRegionIndex >= len(regions):
            focusedRegionIndex = 0

        # [[[TODO: WDW - perhaps if a text area was created, we should
        # give focus to it.]]]
        #
        return [regions, regions[focusedRegionIndex]]

    def _getBrailleRegionsForMenuItem(self, obj):
        """Get the braille for a menu item.

        Arguments:
        - obj: the menu item

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForMenuItem", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                     _getBrailleRegionsForMenuItem(self, obj)
        
        if not self._script.inDocumentContent():
            return braillegenerator.BrailleGenerator.\
                       _getBrailleRegionsForMenuItem(self, obj)

        regions = []

        # Displaying "menu item" for a combo box can confuse users. Therefore,
        # display the combo box role instead.  Also, only do it if the menu
        # item is not focused (if the menu item is focused, it means we're
        # navigating in the combo box).
        #
        label = self._script.getDisplayedLabel(obj)
        focusedRegionIndex = 0
        if label and len(label):
            regions.append(braille.Region(label + " "))
            focusedRegionIndex = 1
        regions.append(braille.Region(obj.name))

        comboBox = \
                 self._script.getAncestor(obj,
                                          [pyatspi.ROLE_COMBO_BOX],
                                          [pyatspi.ROLE_DOCUMENT_FRAME])
        if comboBox \
           and not obj.getState().contains(pyatspi.STATE_FOCUSED) \
           and (settings.brailleVerbosityLevel == \
                settings.VERBOSITY_LEVEL_VERBOSE):
            regions.append(braille.Region(
                " " + rolenames.getBrailleForRoleName(comboBox)))

        return [regions, regions[focusedRegionIndex]]

    def _getBrailleRegionsForList(self, obj):
        """Get the braille for a list in a form.  If the list already has
        focus, then only the selection is displayed.

        Arguments:
        - obj: the list

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForList", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                       _getBrailleRegionsForList(self, obj)
        
        if not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            return braillegenerator.BrailleGenerator.\
                       _getBrailleRegionsForList(self, obj)

        regions = []
        focusedRegionIndex = 0

        if obj.getState().contains(pyatspi.STATE_FOCUSED):
            label = self._script.getDisplayedLabel(obj)
            if not label:
                label = obj.name

            if label and len(label):
                regions.append(braille.Region(label + " "))
                focusedRegionIndex = 1

            item = None
            selection = obj.querySelection()
            for i in xrange(obj.childCount):
                if selection.isChildSelected(i):
                    item = obj[i]
                    break
            if not item:
                item = obj[0]
            regions.append(braille.Region(item.name + " "))

        if settings.brailleVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            regions.append(braille.Region(
                rolenames.getBrailleForRoleName(obj)))

        return [regions, regions[focusedRegionIndex]]

    def _getBrailleRegionsForImage(self, obj):
        """Get the braille regions for an image.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForImage", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                       _getBrailleRegionsForImage(self, obj)
        
        regions = []

        text = ""
        text = self._script.appendString(text, 
                                         self._script.getDisplayedLabel(obj))
        text = self._script.appendString(text, 
                                         self._script.getDisplayedText(obj))

        # If there's no text for the link, expose part of the
        # link to the user if the image is in a link.
        #
        link = self._script.getAncestor(obj, 
                                        [pyatspi.ROLE_LINK], 
                                        [pyatspi.ROLE_DOCUMENT_FRAME])
        if len(text) == 0:
            if link:
                [linkRegions, focusedRegion] = \
                    self._getBrailleRegionsForLink(link)
                for region in linkRegions:
                    text += region.string
        elif link:
            text = self._script.appendString(text, self._getTextForRole(link))

        text = self._script.appendString(text,
                                         self._script.getTextForValue(obj))
        text = self._script.appendString(text, self._getTextForRole(obj))

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]

    def _getBrailleRegionsForLink(self, obj):
        """Gets text to be displayed for a link.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForLink", obj)

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return braillegenerator.BrailleGenerator.\
                       _getDefaultBrailleRegions(self, obj)
        
        regions = []

        text = ""
        text = self._script.appendString(text, 
                                         self._script.getDisplayedLabel(obj))
        text = self._script.appendString(text, 
                                         self._script.getDisplayedText(obj))

        # If there's no text for the link, expose part of the
        # URI to the user.
        #
        if len(text) == 0:
            basename = self._script.getLinkBasename(obj)
            if basename:
                text = basename

        text = self._script.appendString(text,
                                         self._script.getTextForValue(obj))
        text = self._script.appendString(text, self._getTextForRole(obj))

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]
