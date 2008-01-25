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

# [[[TODO: WDW - Pylint is giving us a bunch of errors along these
# lines throughout this file:
#
# E1103:4241:Script.updateBraille: Instance of 'list' has no 'getRole'
# member (but some types could not be inferred)
# 
# I don't know what is going on, so I'm going to tell pylint to
# disable those messages for Gecko.py.]]]
# 
# pylint: disable-msg=E1103

"""Custom script for Gecko toolkit.  NOT WORKING WELL AT THE MOMENT.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import atk
import gtk
import math
import pyatspi
import re
import urlparse

import braille
import braillegenerator
import debug
import default
import input_event
import keybindings
import liveregions
import mag
import orca
import orca_state
import rolenames
import settings
import speech
import speechgenerator
import speechserver
import where_am_I
import bookmarks

from orca_i18n import _
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import Q_        # to provide qualified translatable strings

# Temporary debugging/testing setting.  If True, use the experimental
# performance enhancements.
#
performanceEnhancements = True

# Temporary debugging/testing setting.  If True, use the experimental
# methods to find the next/previous line.
#
useNewLineNav = True

# If True, it tells us to take over caret navigation.  This is something
# that can be set in user-settings.py:
#
# import orca.Gecko
# orca.Gecko.controlCaretNavigation = True
#
controlCaretNavigation = True

# If True, it tells us to position the caret at the beginning of a
# line when arrowing up and down.  If False, we'll try to position the
# caret directly above or below the current caret position.
#
arrowToLineBeginning = True

# If True, it tells Orca to automatically perform a SayAll operation
# when a page is first loaded.
#
sayAllOnLoad = True

# Whether or not to use the structrual navigation commands (e.g. H
# for heading, T for table, and so on).
#
structuralNavigationEnabled = True

# Whether or not to speak the cell's coordinates when navigating
# from cell to cell in HTML tables.
#
speakCellCoordinates = True

# Whether or not to speak the number of cells spanned by a cell
# that occupies more than one row or column of an HTML table.
#
speakCellSpan = True

# Whether or not to announce the header that applies to the current
# when navigating from cell to cell in HTML tables.
#
speakCellHeaders = True

# Whether blank cells should be skipped when navigating in an HTML
# table using table navigation commands
#
skipBlankCells = False

# Whether or not Orca should speak the changing location within the
# document frame *during* a find (i.e. while focus is still in the
# Find toolbar).
#
speakResultsDuringFind = True

# The minimum number of characters that must be matched during
# a find before Orca speaks the changed location, assuming that
# speakResultsDuringFind is True.
#
minimumFindLength = 4

# Whether or not to continue speaking the same line if the match
# has not changed with additional keystrokes.  This setting comes
# in handy for fast typists who might inadvertantly interrupt the
# speaking of the line that matches by continuing to type in the
# Find entry.  This is the equivalent of what we do in autocompletes
# throughout GNOME.  For power-users of the Find toolbar, however,
# that may be too verbose so it's configurable.
#
onlySpeakChangedLinesDuringFind = False

# The minimum number of characters of text that an accessible object must 
# contain to be considered a match in go to next/prev large object
largeObjectTextLength = 75

# Roles that imply their text starts on a new line.
#
NEWLINE_ROLES = [pyatspi.ROLE_PARAGRAPH,
                 pyatspi.ROLE_SEPARATOR,
                 pyatspi.ROLE_LIST_ITEM,
                 pyatspi.ROLE_HEADING]

# Roles that represent a logical chunk of information in a document
#
OBJECT_ROLES = [pyatspi.ROLE_HEADING,
                pyatspi.ROLE_PARAGRAPH,
                pyatspi.ROLE_TABLE,
                pyatspi.ROLE_TABLE_CELL,
                pyatspi.ROLE_TEXT,
                pyatspi.ROLE_SECTION,
                pyatspi.ROLE_DOCUMENT_FRAME,
                pyatspi.ROLE_AUTOCOMPLETE]

ARIA_LANDMARKS = ["banner", "contentinfo", "definition", "main", "navigation",
                  "note", "search", "secondary", "seealso"]

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

        # get the Braille indicator
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            indicatorIndex = 2
        elif state.contains(pyatspi.STATE_CHECKED):
            indicatorIndex = 1
        else:
            indicatorIndex = 0
        text = self._script.appendString(
            settings.brailleCheckBoxIndicators[indicatorIndex],
            text)

        text = self._script.appendString(text, self._getTextForRole(obj))

        regions = []
        componentRegion = braille.Component(obj, text)
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

        indicatorIndex = 0 + obj.getState().contains(pyatspi.STATE_CHECKED)
        text = self._script.appendString(
            settings.brailleRadioButtonIndicators[indicatorIndex],
            text)

        text = self._script.appendString(text, self._getTextForRole(obj))

        regions = []
        componentRegion = braille.Component(obj, text)
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
            for child in menu:
                if child.getState().contains(pyatspi.STATE_SELECTED):
                    regions.append(braille.Region(child.name))
                    break

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

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Provides a speech generator specific to Gecko.
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)
        self.speechGenerators[pyatspi.ROLE_DOCUMENT_FRAME] = \
             self._getSpeechForDocumentFrame
        self.speechGenerators[pyatspi.ROLE_ENTRY]          = \
             self._getSpeechForText
        self.speechGenerators[pyatspi.ROLE_LINK]           = \
             self._getSpeechForLink
        self.speechGenerators[pyatspi.ROLE_LIST_ITEM]      = \
             self._getSpeechForListItem
        self.speechGenerators[pyatspi.ROLE_SLIDER]         = \
             self._getSpeechForSlider

    def getSpeechForObjectRole(self, obj, role=None):
        """Prevents some roles from being spoken."""
        if obj.getRole() in [pyatspi.ROLE_PARAGRAPH,
                             pyatspi.ROLE_SECTION,
                             pyatspi.ROLE_LABEL,
                             pyatspi.ROLE_LIST_ITEM,
                             pyatspi.ROLE_MENU_ITEM,
                             pyatspi.ROLE_UNKNOWN]:
            return []
        else:
            return [rolenames.getSpeechForRoleName(obj, role)]

    def _getSpeechForDocumentFrame(self, obj, already_focused):
        """Gets the speech for a document frame.

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        name = obj.name
        if name and len(name):
            utterances.append(name)
        utterances.extend(self.getSpeechForObjectRole(obj))

        self._debugGenerator("Gecko._getSpeechForDocumentFrame",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForText(self, obj, already_focused):
        """Gets the speech for an autocomplete box.

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForText(self, obj, already_focused)
        
        utterances = []
        parent = obj.parent
        if parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            # This is the main difference between this class and the default
            # class - we'll give this thing a name here, and we'll make it
            # be the name of the autocomplete.
            #
            label = self._script.getDisplayedLabel(parent)
            if not label or not len(label):
                label = parent.name
            utterances.append(label)
        elif obj.getRole() in [pyatspi.ROLE_ENTRY,
                               pyatspi.ROLE_PASSWORD_TEXT] \
            and self._script.inDocumentContent():
            # This is a form field in web content.  If we don't get a label,
            # we'll try to guess what text on the page is functioning as
            # the label.
            #
            label = self._script.getDisplayedLabel(obj)
            if not label or not len(label):
                label = self._script.guessTheLabel(obj)
            if label:
                utterances.append(label)
        else:
            return speechgenerator.SpeechGenerator._getSpeechForText(
                self, obj, already_focused)

        utterances.extend(self.getSpeechForObjectRole(obj))

        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        utterances.append(text)

        self._debugGenerator("Gecko._getSpeechForText",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForComboBox(self, obj, already_focused)
        
        utterances = []

        label = self._script.getDisplayedLabel(obj)
        if not label:
            if not self._script.inDocumentContent():
                label = obj.name
            else:
                label = self._script.guessTheLabel(obj)

        if not already_focused and label:
            utterances.append(label)

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
            for child in menu:
                if child.getState().contains(pyatspi.STATE_SELECTED):
                    utterances.append(child.name)
                    break

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        if not already_focused:
            utterances.extend(self.getSpeechForObjectRole(obj))

        self._debugGenerator("Gecko._getSpeechForComboBox",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForMenuItem(self, obj, already_focused)
        
        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForMenuItem(self, obj, already_focused)

        utterances = self._getSpeechForObjectName(obj)

        # Saying "menu item" for a combo box can confuse users. Therefore,
        # speak the combo box role instead.  Also, only do it if the menu
        # item is not focused (if the menu item is focused, it means we're
        # navigating in the combo box)
        #
        if not obj.getState().contains(pyatspi.STATE_FOCUSED):
            comboBox = \
                 self._script.getAncestor(obj,
                                          [pyatspi.ROLE_COMBO_BOX],
                                          [pyatspi.ROLE_DOCUMENT_FRAME])
            if comboBox:
                utterances.extend(self.getSpeechForObjectRole(comboBox))

        self._debugGenerator("Gecko._getSpeechForMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForListItem(self, obj, already_focused):
        """Get the speech for a list item.

        Arguments:
        - obj: the list item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #

        if self._script.isAriaWidget(obj) \
           or not self._script.inDocumentContent(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForListItem(self, obj, already_focused)
        
        if not obj.getState().contains(pyatspi.STATE_SELECTABLE):
            return speechgenerator.SpeechGenerator.\
                       _getDefaultSpeech(self, obj, already_focused)

        utterances = self._getSpeechForObjectName(obj)

        self._debugGenerator("Gecko._getSpeechForListItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForList(self, obj, already_focused):
        """Get the speech for a list.

        Arguments:
        - obj: the list
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForList(self, obj, already_focused)
        
        if not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForList(self, obj, already_focused)

        utterances = []

        if obj.getState().contains(pyatspi.STATE_FOCUSED):
            label = self._script.getDisplayedLabel(obj)
            if not label:
                if not self._script.inDocumentContent():
                    label = obj.name
                else:
                    label = self._script.guessTheLabel(obj)

            if not already_focused and label:
                utterances.append(label)

            item = None
            selection = obj.querySelection()
            for i in xrange(obj.childCount):
                if selection.isChildSelected(i):
                    item = obj[i]
                    break
            item = item or obj[0]
            if item:
                name = self._getSpeechForObjectName(item)
                if name != label:
                    utterances.extend(name)

        if not already_focused:
            if obj.getState().contains(pyatspi.STATE_MULTISELECTABLE):
                # Translators: "multi-select" refers to a web form list
                # in which more than one item can be selected at a time.
                #
                utterances.append(_("multi-select"))

            # Translators: this represents a list in HTML.
            #
            itemString = ngettext("List with %d item",
                                  "List with %d items",
                                  obj.childCount) % obj.childCount
            utterances.append(itemString)

        self._debugGenerator("Gecko._getSpeechForList",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForImage(self, obj, already_focused):
        """Gets a list of utterances to be spoken for an image.

        The default speech will be of the following form:

        label name role availability

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForImage(self, obj, already_focused)
        
        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)

            # If there's no text for the image, expose the link to
            # the user if the image is in a link.
            #
            link = self._script.getAncestor(obj,
                                            [pyatspi.ROLE_LINK],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])
            if not len(utterances):
                if link:
                    utterances.extend(self._getSpeechForLink(link,
                                                             already_focused))
            elif link:
                utterances.extend(self.getSpeechForObjectRole(link))

            utterances.extend(self.getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForImage",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForLink(self, obj, already_focused):
        """Gets a list of utterances to be spoken for a link.

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.getSpeech(obj,
                                                             already_focused)
        
        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)

            # Handle empty alt tags.
            #
            if name:
                lengthOfName = len(name[0].strip())
                if (lengthOfName > 0) and (name != label):
                    utterances.extend(name)

            # If there's no text for the link, expose part of the
            # URI to the user.
            #
            if not len(utterances):
                basename = self._script.getLinkBasename(obj)
                if basename:
                    utterances.append(basename)

            utterances.extend(self.getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForLink",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForTable(self, obj, already_focused)
        
        # [[[TODO: JD - We should decide if we want to provide
        # information about the table dimensions, whether or not
        # this is a layout table versus a data table, etc.  For now,
        # however, if it's in HTML content let's ignore it so that
        # SayAll by sentence works. :-) ]]]
        #
        utterances = []

        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForTable(self, obj, already_focused)

        return utterances

    def _getSpeechForRadioButton(self, obj, already_focused):
        """Get the speech for a radio button.  If the button already had
        focus, then only the state is spoken.

        Arguments:
        - obj: the radio button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForRadioButton(self, obj, already_focused)
        
        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForRadioButton(self, obj, already_focused)

        utterances = []
        if obj.getState().contains(pyatspi.STATE_CHECKED):
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

        if not already_focused:
            # The label is handled as a context in default.py -- assuming we
            # don't have to guess it.  If  we need to guess it, we need to
            # add it to utterances.
            #
            label = self._script.getDisplayedLabel(obj)
            if not label:
                label = self._script.guessTheLabel(obj)
                if label:
                    utterances.append(label)

            utterances.append(selectionState)
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(selectionState)

        self._debugGenerator("Gecko._getSpeechForRadioButton",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForCheckBox(self, obj, already_focused)
        
        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForCheckBox(self, obj, already_focused)

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

        # If it's not already focused, say its label.
        #
        if not already_focused:
            label = self._script.getDisplayedLabel(obj)
            if not label:
                label = self._script.guessTheLabel(obj)
            if label:
                utterances.append(label)
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(checkedState)
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(checkedState)

        self._debugGenerator("Gecko._getSpeechForCheckBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

        Arguments:
        - obj: the object
        - stopAncestor: the ancestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if obj is stopAncestor:
            return utterances

        parent = obj.parent
        while parent and (parent.parent != parent):
            if self._script.isSameObject(parent, stopAncestor):
                break

            # We try to omit layout things right off the bat.
            #
            if self._script.isLayoutOnly(parent):
                parent = parent.parent
                continue

            # If the rolename is unknown, skip this item.
            #
            if parent.getRole() == pyatspi.ROLE_UNKNOWN:
                parent = parent.parent
                continue

            # To be consistent with how we provide access to other
            # applications, don't speak the name of menu bars.
            #
            if parent.getRole() == pyatspi.ROLE_MENU_BAR:
                parent = parent.parent
                continue

            # Skip unfocusable menus.  This is for earlier versions
            # of Firefox where menus were nested in kind of an odd
            # dual nested menu hierarchy.
            #
            if (parent.getRole() == pyatspi.ROLE_MENU) \
               and not parent.getState().contains(pyatspi.STATE_FOCUSABLE):
                parent = parent.parent
                continue

            # Now...autocompletes are weird.  We'll let the handling of
            # the entry give us the name -- unless we're in a toolbar.
            #
            containingToolbar = \
                  self._script.getAncestor(obj,
                                           [pyatspi.ROLE_TOOL_BAR],
                                           [pyatspi.ROLE_DOCUMENT_FRAME])
            if parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE and \
               not containingToolbar:
                parent = parent.parent
                continue

            # Labels with children should be ignored.  (This is the
            # bugzilla form bogusity bug.)
            #
            if parent.getRole() == pyatspi.ROLE_LABEL:
                parent = parent.parent
                continue
                
            # Well...now we skip the parent if it's accessible text is
            # a single EMBEDDED_OBJECT_CHARACTER.  The reason for this
            # is that it Script.getDisplayedText will end up coming
            # back to the children of an object for the text in the
            # children if an object's text contains an
            # EMBEDDED_OBJECT_CHARACTER.
            #
            parentText = self._script.queryNonEmptyText(parent)
            if parentText:
                displayedText = parentText.getText(0, -1)
                unicodeText = displayedText.decode("UTF-8")
                if unicodeText \
                    and (len(unicodeText) == 1) \
                    and (unicodeText[0] == \
                                     self._script.EMBEDDED_OBJECT_CHARACTER):
                    parent = parent.parent
                    continue

            # Finally, put in the text and label (if they exist)
            #
            text = self._script.getDisplayedText(parent)
            label = self._script.getDisplayedLabel(parent)
            newUtterances = []
            if text and (text != label) and len(text.strip()) \
                and (not text.startswith("chrome://")):
                newUtterances.append(text)
            if label and len(label.strip()):
                newUtterances.append(label)

            # Well...if we made it this far, we will now append the
            # role, then the text, and then the label.
            #
            if not parent.getRole() in [pyatspi.ROLE_TABLE_CELL,
                                        pyatspi.ROLE_FILLER] \
                and len(newUtterances):
                utterances.append(rolenames.getSpeechForRoleName(parent))

            utterances.extend(newUtterances)

            parent = parent.parent

        utterances.reverse()

        return utterances
            
    def _getSpeechForSlider(self, obj, already_focused):
        """Get the speech for a slider.  If the object already
        had focus, just the value is spoken.

        Arguments:
        - obj: the slider
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """
        
        # Let default handle non-ARIA widgets (XUL?)
        if not self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForSlider(self, obj, already_focused)

        value = obj.queryValue()

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
            minimumIncrement = 0.0

        if minimumIncrement == 0.0:
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
            utterances = []
            utterances.extend(self._getSpeechForObjectLabel(obj))
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(valueString)
            utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getSpeechForSlider",
                             obj,
                             already_focused,
                             utterances)

        return utterances
                        
########################################################################
#                                                                      #
# Custom WhereAmI                                                      #
#                                                                      #
######################################################################## 

class GeckoWhereAmI(where_am_I.WhereAmI):
    def __init__(self, script):
        """Gecko specific WhereAmI that will be used to speak information
        about the current object of interest and will provide additional Gecko
        specific information.
        """
        where_am_I.WhereAmI.__init__(self, script)
        self._script = script
        
    def whereAmI(self, obj, doubleClick, statusOrTitle):
        """Calls the base class method for single clicks and Gecko specific
        information presentation methods for double clicks
        """

        if not doubleClick or statusOrTitle \
           or not self._script.inDocumentContent(obj):
            where_am_I.WhereAmI.whereAmI(self, obj, doubleClick, statusOrTitle)
            self._script.liveMngr.outputLiveRegionDescription(obj)
        else:
            try:
                self._collectionPageSummary()
            except:
                self._iterativePageSummary(obj)

    def _speakDefaultButton(self, obj):
        """Speaks the default button in a dialog.

        Arguments:
        - obj: the dialog box for which the default button should be obtained
        """

        if not (self._script.inDocumentContent(orca_state.locusOfFocus) \
                and not self._script.isAriaWidget(orca_state.locusOfFocus)):
            where_am_I.WhereAmI._speakDefaultButton(self, obj)

    def _collectionPageSummary(self):
        """Uses the Collection interface to get the quantity of headings, 
        forms, tables, visited and unvisited links.
        """
        docframe = self._script.getDocumentFrame()
        col = docframe.queryCollection()

        # We will initialize these after the queryCollection() call in case
        # Collection is not supported
        headings = 0 
        forms = 0
        tables = 0
        vlinks = 0
        uvlinks = 0

        stateset = pyatspi.StateSet()
        roles = [pyatspi.ROLE_HEADING, pyatspi.ROLE_LINK, pyatspi.ROLE_TABLE,
                 pyatspi.ROLE_FORM]
        rule = col.createMatchRule(stateset.raw(), col.MATCH_NONE,  
                                   "", col.MATCH_NONE,
                                   roles, col.MATCH_ANY,
                                   "", col.MATCH_NONE,
                                   False)

        matches = col.getMatches (rule, col.SORT_ORDER_CANONICAL, 0)
        col.freeMatchRule(rule)
        for obj in matches:
            role = obj.getRole()
            if role == pyatspi.ROLE_HEADING:
                headings += 1
            elif role == pyatspi.ROLE_FORM:
                forms += 1
            elif role == pyatspi.ROLE_TABLE \
                      and not self._script.isLayoutOnly(obj):
                tables += 1
            elif role == pyatspi.ROLE_LINK:
                if obj.getState().contains(pyatspi.STATE_VISITED):
                    vlinks += 1
                else:
                    uvlinks += 1

        self._outputPageSummary(headings, forms, tables, vlinks, uvlinks, None)
            
    def _iterativePageSummary(self, obj):
        """Reads the quantity of headings, forms, tables, visited and 
        unvisited links.
        """
        headings = 0 
        forms = 0
        tables = 0
        vlinks = 0
        uvlinks = 0
        nodetotal = 0
        obj_index = None
        currentobj = obj

        # start at the first object after document frame
        obj = self._script.getDocumentFrame()[0]
        while obj:
            nodetotal += 1
            if obj == currentobj:
                obj_index = nodetotal
            role = obj.getRole()
            if role == pyatspi.ROLE_HEADING:
                headings += 1
            elif role == pyatspi.ROLE_FORM:
                forms += 1
            elif role == pyatspi.ROLE_TABLE \
                      and not self._script.isLayoutOnly(obj):
                tables += 1
            elif role == pyatspi.ROLE_LINK:
                if obj.getState().contains(pyatspi.STATE_VISITED):
                    vlinks += 1
                else:
                    uvlinks += 1

            obj = self._script.findNextObject(obj)

        # Calculate the percentage of the document that has been read.
        if obj_index:
            percentread = int(obj_index*100/nodetotal)
        else:
            percentread = None

        self._outputPageSummary(headings, forms, tables, 
                               vlinks, uvlinks, percentread)

    def _outputPageSummary(self, headings, forms, tables, 
                                 vlinks, uvlinks, percent):

        utterances = []
        if headings:
            # Translators: Announces the number of headings in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d heading', '%d headings', headings) %headings)
        if forms:
            # Translators: Announces the number of forms in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d form', '%d forms', forms) %forms)
        if tables:
            # Translators: Announces the number of non-layout tables in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d table', '%d tables', tables) %tables)
        if vlinks:
            # Translators: Announces the number of visited links in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d visited link', '%d visited links', vlinks) %vlinks)
        if uvlinks:
            # Translators: Announces the number of unvisited links in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d unvisited link', '%d unvisited links', uvlinks) %uvlinks)
        if percent is not None:
            # Translators: Announces the percentage of the document that has
            # been read.  This is calculated by knowing the index of the 
            # current position divided by the total number of objects on the 
            # page.
            # 
            utterances.append(_('%d percent of document read') %percent)

        speech.speakUtterances(utterances)  


####################################################################
#                                                                  #
# Custom bookmarks class                                           #
#                                                                  #
####################################################################
class GeckoBookmarks(bookmarks.Bookmarks):
    def __init__(self, script):
        bookmarks.Bookmarks.__init__(self, script)
        self._currentbookmarkindex = {}
        
        
    def addBookmark(self, inputEvent):
        """ Add an in-page accessible object bookmark for this key and
        webpage URI. """ 
        # form bookmark dictionary key
        index = (inputEvent.hw_code, self.getURIKey())
        # convert the current object to a path and bookmark it
        obj, characterOffset = self._script.getCaretContext()
        path = self._objToPath()
        self._bookmarks[index] = path, characterOffset
        # Translators: this announces that a bookmark has been entered
        #
        utterances = [(_('entered bookmark'))]
        utterances.extend(self._script.speechGenerator.getSpeech \
                         (obj, False))
        speech.speakUtterances(utterances)
        
    def goToBookmark(self, inputEvent, index=None):
        """ Go to the bookmark indexed at this key and this page's URI """
        index = index or (inputEvent.hw_code, self.getURIKey())
        
        try:
            path, characterOffset = self._bookmarks[index]
        except KeyError:
            self._script.systemBeep()
            return
        # convert our path to an object
        obj = self.pathToObj(path)
       
        if obj:
            # restore the location
            self._script.setCaretPosition(obj, characterOffset)
            self._script.updateBraille(obj)
            self._script.speakContents( \
                self._script.getObjectContentsAtOffset(obj, characterOffset))
            # update the currentbookmark
            self._currentbookmarkindex[index[1]] = index[0]
        else:
            self._script.systemBeep()
        
    def bookmarkCurrentWhereAmI(self, inputEvent):
        """ Report "Where am I" information for this bookmark relative to the 
        current pointer location."""
        index = (inputEvent.hw_code, self.getURIKey())
        try:
            path, characterOffset = self._bookmarks[index]
            obj = self.pathToObj(path)
        except KeyError:
            self._script.systemBeep()
            return
            
        [cur_obj, cur_characterOffset] = self._script.getCaretContext()
        
        # Are they the same object?
        if self._script.isSameObject(cur_obj, obj):
            # Translators: this announces that the current object is the same
            # object pointed to by the bookmark.
            #
            speech.speak(_('bookmark is current object'))
            return
        # Are their parents the same?
        elif self._script.isSameObject(cur_obj.parent, obj.parent):
            # Translators: this announces that the current object's parent and 
            # the parent of the object pointed to by the bookmark are the same.
            #
            speech.speak(_('bookmark and current object have same parent'))
            return
        
        # Do they share a common ancestor?
        # bookmark's ancestors
        bookmark_ancestors = []
        p = obj.parent
        while p:
            bookmark_ancestors.append(p)
            p = p.parent
        # look at current object's ancestors to compare to bookmark's ancestors
        p = cur_obj.parent
        while p:
            if bookmark_ancestors.count(p) > 0:
                # Translators: this announces that the bookmark and the current
                # object share a common ancestor
                #
                speech.speak(_('shared ancestor %s') %p.getRole())
                return
            p = p.parent
        
        # Translators: This announces that a comparison between the bookmark
        # and the current object can not be determined.
        #
        speech.speak(_('comparison unknown'))
        
    def saveBookmarks(self, inputEvent):
        """ Save the bookmarks for this script. """
        saved = {}
         
        # save obj as a path instead of an accessible
        for index, bookmark in self._bookmarks.iteritems():
            saved[index] = bookmark[0], bookmark[1]
            
        try:
            self.saveBookmarksToDisk(saved)
            # Translators: this announces that a bookmark has been saved to 
            # disk
            #
            speech.speak(_('bookmarks saved'))
        except IOError:
            # Translators: this announces that a bookmark could not be saved to 
            # disk
            #
            speech.speak(_('bookmarks could not be saved'))

        # Notify the observers
        for o in self._saveObservers:
            o()
            
    def goToNextBookmark(self, inputEvent):
        """ Go to the next bookmark location.  If no bookmark has yet to be
        selected, the first bookmark will be used.  """
        # The convenience of using a dictionary to add/goto a bookmark is 
        # offset by the difficulty in finding the next bookmark.  We will 
        # need to sort our keys to determine the next bookmark on a page by 
        # page basis.
        bm_keys = self._bookmarks.keys()
        current_uri = self.getURIKey()
        
        # mine out the hardware keys for this page and sort them
        thispage_hwkeys = []
        for bm_key in bm_keys:
            if bm_key[1] == current_uri:
                thispage_hwkeys.append(bm_key[0])
        thispage_hwkeys.sort()
        
        # no bookmarks for this page
        if len(thispage_hwkeys) == 0:
            self._script.systemBeep()
            return
        # only 1 bookmark or we are just starting out
        elif len(thispage_hwkeys) == 1 or \
                         not self._currentbookmarkindex.has_key(current_uri):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            return
        
        # find current bookmark hw_code in our sorted list.  
        # Go to next one if possible
        try:
            index = thispage_hwkeys.index( \
                                 self._currentbookmarkindex[current_uri])
            self.goToBookmark(None, index=( \
                                 thispage_hwkeys[index+1], current_uri))
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            
    def goToPrevBookmark(self, inputEvent):
        """ Go to the previous bookmark location.  If no bookmark has yet to be
        selected, the first bookmark will be used.  """
        bm_keys = self._bookmarks.keys()
        current_uri = self.getURIKey()
        
        # mine out the hardware keys for this page and sort them
        thispage_hwkeys = []
        for bm_key in bm_keys:
            if bm_key[1] == current_uri:
                thispage_hwkeys.append(bm_key[0])
        thispage_hwkeys.sort()
        
        # no bookmarks for this page
        if len(thispage_hwkeys) == 0:
            self._script.systemBeep()
            return
        # only 1 bookmark or we are just starting out
        elif len(thispage_hwkeys) == 1 or \
                         not self._currentbookmarkindex.has_key(current_uri):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            return
        
        # find current bookmark hw_code in our sorted list.  
        # Go to next one if possible
        try:
            index = thispage_hwkeys.index( \
                            self._currentbookmarkindex[current_uri])
            self.goToBookmark(None, 
                              index=(thispage_hwkeys[index-1], current_uri))
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))    
            
    def _objToPickle(self, obj=None):
        """Given an object, return it's saving (pickleable) format.  In this 
        case, the obj path is determined relative to the document frame and is 
        returned as a list.  If obj is not provided, the current caret context
        is used.  """
        return self._objToPath(start_obj=obj)
                               
    def _objToPath(self, start_obj=None):
        """Given an object, return it's path from the root accessible.  If obj 
        is not provided, the current caret context is used. """
        if not start_obj:
            [start_obj, characterOffset] = self._script.getCaretContext()    
            
        if start_obj is None \
                     or start_obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            return []
        else:
            path = []
            path.append(start_obj.getIndexInParent())
            p = start_obj.parent
            while p:
                if p.getRole()  == pyatspi.ROLE_DOCUMENT_FRAME:
                    path.reverse()
                    return path
                path.append(p.getIndexInParent())
                p = p.parent
            
            return []
            
    def _pickleToObj(self, obj):
        """Return the s with the given path (relative to the
        document frame). """
        
        # could test for different obj types.  We'll just assume it is
        # list that represents a path for now.
        return self.pathToObj(obj)
            
    def pathToObj(self, path):
        """Return the object with the given path (relative to the
        document frame). """
        returnobj = self._script.getDocumentFrame()
        for childnumber in path:
            try:
                returnobj = returnobj[childnumber]
            except IndexError:
                return None
            
        return returnobj
            
    def getURIKey(self):
        """Returns the URI key for a given page as a URI stripped of 
        parameters?query#fragment as seen in urlparse."""
        uri = self._script.getDocumentFrameURI()
        parsed_uri = urlparse.urlparse(uri)
        return ''.join(parsed_uri[0:3])
            
    
########################################################################
#                                                                      #
# Script                                                               #
#                                                                      #
########################################################################

class Script(default.Script):
    """The script for Firefox.

    NOTE: THIS IS UNDER DEVELOPMENT AND DOES NOT PROVIDE ANY COMPELLING
    ACCESS TO FIREFOX AT THIS POINT.
    """

    ####################################################################
    #                                                                  #
    # Overridden Script Methods                                        #
    #                                                                  #
    ####################################################################

    def __init__(self, app):
        default.Script.__init__(self, app)

        # Initialize variables to make pylint happy.
        #
        self.arrowToLineBeginningCheckButton = None
        self.changedLinesOnlyCheckButton = None
        self.controlCaretNavigationCheckButton = None
        self.minimumFindLengthAdjustment = None
        self.minimumFindLengthLabel = None
        self.minimumFindLengthSpinButton = None
        self.sayAllOnLoadCheckButton = None
        self.skipBlankCellsCheckButton = None
        self.speakCellCoordinatesCheckButton = None
        self.speakCellHeadersCheckButton = None
        self.speakCellSpanCheckButton = None
        self.speakResultsDuringFindCheckButton = None
        self.structuralNavigationCheckButton = None
        self.targetCharacterExtents = (0, 0, 0, 0)

        # _caretNavigationFunctions are functions that represent fundamental
        # ways to move the caret (e.g., by the arrow keys).
        #
        self._caretNavigationFunctions = \
            [Script.goNextCharacter,
             Script.goPreviousCharacter,
             Script.goNextWord,
             Script.goPreviousWord,
             Script.goNextLine,
             Script.goPreviousLine,
             Script.expandComboBox]

        # _structuralNavigationFunctions are functions that represent
        # more complex navigation functions (e.g., moving by heading,
        # large object, etc.).
        #
        self._structuralNavigationFunctions = \
            [Script.goNextHeading,
             Script.goPreviousHeading,
             Script.goNextHeading1,
             Script.goPreviousHeading1,
             Script.goNextHeading2,
             Script.goPreviousHeading2,
             Script.goNextHeading3,
             Script.goPreviousHeading3,
             Script.goNextHeading4,
             Script.goPreviousHeading4,
             Script.goNextHeading5,
             Script.goPreviousHeading5,
             Script.goNextHeading6,
             Script.goPreviousHeading6,
             Script.goNextChunk,
             Script.goPreviousChunk,
             Script.goNextLandmark,
             Script.goPreviousLandmark,
             Script.goNextList,
             Script.goPreviousList,
             Script.goNextListItem,
             Script.goPreviousListItem,
             Script.goNextUnvisitedLink,
             Script.goPreviousUnvisitedLink,
             Script.goNextVisitedLink,
             Script.goPreviousVisitedLink,
             Script.goNextFormField,
             Script.goPreviousFormField,
             Script.goNextBlockquote,
             Script.goPreviousBlockquote,
             Script.goNextTable,
             Script.goPreviousTable,
             Script.goNextLiveRegion,
             Script.goPreviousLiveRegion,
             Script.goLastLiveRegion,
             Script.advanceLivePoliteness,
             Script.setLivePolitenessOff,
             Script.monitorLiveRegions,
             Script.reviewLiveAnnouncement,
             Script.goCellLeft,
             Script.goCellRight,
             Script.goCellUp,
             Script.goCellDown,
             Script.goCellFirst,
             Script.goCellLast]

        if controlCaretNavigation:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Orca is controlling the caret.")
        else:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Gecko is controlling the caret.")

        # We keep track of whether we're currently in the process of
        # loading a page.
        #
        self._loadingDocumentContent = False

        # In tabbed content (i.e., Firefox's support for one tab per
        # URL), we also keep track of the caret context in each tab.
        # the key is the document frame and the value is the caret
        # context for that frame.
        #
        self._documentFrameCaretContext = {}

        # When navigating in a non-uniform table, one can move to a
        # cell which spans multiple rows and/or columns.  When moving
        # beyond that cell, into a cell that does NOT span multiple
        # rows/columns, we want to be sure we land in the right place.
        # Therefore, we'll store the coordinates from "our perspective."
        #
        self.lastTableCell = [-1, -1]

        # During a find we get caret-moved events reflecting the changing
        # screen contents.  The user can opt to have these changes announced.
        # If the announcement is enabled, it still only will be made if the
        # selected text is a certain length (user-configurable) and if the
        # line has changed (so we don't keep repeating the line).  However,
        # the line has almost certainly changed prior to this length being
        # reached.  Therefore, we need to make an initial announcement, which
        # means we need to know if that has already taken place.
        #
        self.madeFindAnnouncement = False

        # We need to be able to distinguish focus events that are triggered
        # by the call to grabFocus() in setCaretPosition() from those that
        # are valid.  See bug #471537.
        #
        self._objectForFocusGrab = None
        
        # We don't want to prevent the user from arrowing into an
        # autocomplete when it appears in a search form.  We need to
        # keep track if one has appeared or disappeared.
        #
        self._autocompleteVisible = False

        # Create the live region manager and start the message manager
        self.liveMngr = liveregions.LiveRegionManager(self)

        # We want to keep track of the line contents we just got so that
        # we can speak and braille this information without having to call
        # getLineContentsAtOffset() twice.
        #
        self._previousLineContents = None
        self._currentLineContents = None
        self._nextLineContents = None

    def getWhereAmI(self):
        """Returns the "where am I" class for this script.
        """
        return GeckoWhereAmI(self)
    
    def getBookmarks(self):
        """Returns the "bookmarks" class for this script.
        """
        try:
            return self.bookmarks 
        except AttributeError:
            self.bookmarks = GeckoBookmarks(self)
            return self.bookmarks

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings.
        """

        default.Script.setupInputEventHandlers(self)

        # Debug only.
        #
        self.inputEventHandlers["dumpContentsHandler"] = \
            input_event.InputEventHandler(
                Script.dumpContents,
                "Dumps document content to stdout.")

        self.inputEventHandlers["goNextCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goNextCharacter,
                # Translators: this is for navigating HTML content one
                # character at a time.
                #
                _("Goes to next character."))

        self.inputEventHandlers["goPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousCharacter,
                # Translators: this is for navigating HTML content one
                # character at a time.
                #
               _( "Goes to previous character."))

        self.inputEventHandlers["goNextWordHandler"] = \
            input_event.InputEventHandler(
                Script.goNextWord,
                # Translators: this is for navigating HTML content one
                # word at a time.
                #
                _("Goes to next word."))

        self.inputEventHandlers["goPreviousWordHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousWord,
                # Translators: this is for navigating HTML content one
                # word at a time.
                #
                _("Goes to previous word."))

        self.inputEventHandlers["goNextLineHandler"] = \
            input_event.InputEventHandler(
                Script.goNextLine,
                # Translators: this is for navigating HTML content one
                # line at a time.
                #
                _("Goes to next line."))

        self.inputEventHandlers["goPreviousLineHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousLine,
                # Translators: this is for navigating HTML content one
                # line at a time.
                #
                _("Goes to previous line."))

        self.inputEventHandlers["goTopOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goTopOfFile,
                # Translators: this command will move the user to the
                # beginning of an HTML document.
                #
                _("Goes to the top of the file."))

        self.inputEventHandlers["goBottomOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goBottomOfFile,
                # Translators: this command will move the user to the
                # end of an HTML document.
                #
                _("Goes to the bottom of the file."))

        self.inputEventHandlers["expandComboBoxHandler"] = \
            input_event.InputEventHandler(
                Script.expandComboBox,
                # Translators: this is for causing a collapsed combo box
                # which was reached by Orca's caret navigation to be expanded.
                #
                _("Causes the current combo box to be expanded."))

        self.inputEventHandlers["goCellLeftHandler"] = \
            input_event.InputEventHandler(
                Script.goCellLeft,
                # Translators: this is for navigating inside HTML tables.
                #
                _("Goes left one cell."))

        self.inputEventHandlers["goCellRightHandler"] = \
            input_event.InputEventHandler(
                Script.goCellRight,
                # Translators: this is for navigating inside HTML tables.
                #
                _("Goes right one cell."))

        self.inputEventHandlers["goCellDownHandler"] = \
            input_event.InputEventHandler(
                Script.goCellDown,
                # Translators: this is for navigating inside HTML tables.
                #
                _("Goes down one cell."))

        self.inputEventHandlers["goCellUpHandler"] = \
            input_event.InputEventHandler(
                Script.goCellUp,
                # Translators: this is for navigating inside HTML tables.
                #
                _("Goes up one cell."))

        self.inputEventHandlers["goCellFirstHandler"] = \
            input_event.InputEventHandler(
                Script.goCellFirst,
                # Translators: this is for navigating inside HTML tables.
                #
                _("Goes to the first cell in a table."))

        self.inputEventHandlers["goCellLastHandler"] = \
            input_event.InputEventHandler(
                Script.goCellLast,
                # Translators: this is for navigating inside HTML tables.
                #
                _("Goes to the last cell in a table."))

        self.inputEventHandlers["goPreviousHeadingHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h1>).
                #
                _("Goes to previous heading."))

        self.inputEventHandlers["goNextHeadingHandler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h1>).
                #
                _("Goes to next heading."))

        self.inputEventHandlers["goPreviousHeading1Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading1,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h1>).
                #
                _("Goes to previous heading at level 1."))

        self.inputEventHandlers["goNextHeading1Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading1,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h1>).
                #
                _("Goes to next heading at level 1."))

        self.inputEventHandlers["goPreviousHeading2Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading2,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h2>).
                #
                _("Goes to previous heading at level 2."))

        self.inputEventHandlers["goNextHeading2Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading2,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h2>).
                #
                _("Goes to next heading at level 2."))

        self.inputEventHandlers["goPreviousHeading3Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading3,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h3>).
                #
                _("Goes to previous heading at level 3."))

        self.inputEventHandlers["goNextHeading3Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading3,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h3>).
                #
                _("Goes to next heading at level 3."))

        self.inputEventHandlers["goPreviousHeading4Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading4,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h4>).
                #
                _("Goes to previous heading at level 4."))

        self.inputEventHandlers["goNextHeading4Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading4,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h4>).
                #
                _("Goes to next heading at level 4."))

        self.inputEventHandlers["goPreviousHeading5Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading5,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h5>).
                #
                _("Goes to previous heading at level 5."))

        self.inputEventHandlers["goNextHeading5Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading5,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h5>).
                #
                _("Goes to next heading at level 5."))

        self.inputEventHandlers["goPreviousHeading6Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading6,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h6>).
                #
                _("Goes to previous heading at level 6."))

        self.inputEventHandlers["goNextHeading6Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading6,
                # Translators: this is for navigating HTML by headers
                # (e.g., <h6>).
                #
                _("Goes to next heading at level 6."))

        self.inputEventHandlers["goPreviousChunkHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousChunk,
                # Translators: this is for navigating HTML in a structural
                # manner, where a 'large object' is a logical chunk of
                # text, such as a paragraph, a list, a table, etc.
                #
                _("Goes to previous large object."))

        self.inputEventHandlers["goNextChunkHandler"] = \
            input_event.InputEventHandler(
                Script.goNextChunk,
                # Translators: this is for navigating HTML in a structural
                # manner, where a 'large object' is a logical chunk of
                # text, such as a paragraph, a list, a table, etc.
                #
                _("Goes to next large object."))

        self.inputEventHandlers["goPreviousLandmark"] = \
            input_event.InputEventHandler(
                Script.goPreviousLandmark,
                # Translators: this is for navigating to the previous ARIA
                # role landmark.  ARIA role landmarks are the W3C defined HTML 
                # tag attribute 'role' used to identify important part of 
                # webpage like banners, main context, search etc.
                #
                _("Goes to previous landmark."))

        self.inputEventHandlers["goNextLandmark"] = \
            input_event.InputEventHandler(
                Script.goNextLandmark,
                # Translators: this is for navigating to the next ARIA
                # role landmark.
                #
                _("Goes to next landmark."))

        self.inputEventHandlers["goPreviousListHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousList,
                # Translators: this is for navigating between bulleted/numbered
                # lists in HTML
                #
                _("Goes to previous list."))

        self.inputEventHandlers["goNextListHandler"] = \
            input_event.InputEventHandler(
                Script.goNextList,
                # Translators: this is for navigating between bulleted/numbered
                # lists in HTML
                #
                _("Goes to next list."))

        self.inputEventHandlers["goPreviousListItemHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousListItem,
                # Translators: this is for navigating between bulleted/numbered
                # list items in HTML
                #
                _("Goes to previous list item."))

        self.inputEventHandlers["goNextListItemHandler"] = \
            input_event.InputEventHandler(
                Script.goNextListItem,
                # Translators: this is for navigating between bulleted/numbered
                # list items in HTML
                #
                _("Goes to next list item."))

        self.inputEventHandlers["goPreviousUnvisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousUnvisitedLink,
                # Translators: this is for navigating between links in HTML
                #
                _("Goes to previous unvisited link."))

        self.inputEventHandlers["goNextUnvisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goNextUnvisitedLink,
                # Translators: this is for navigating between links in HTML
                #
               _("Goes to next unvisited link."))

        self.inputEventHandlers["goPreviousVisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousVisitedLink,
                # Translators: this is for navigating between links in HTML
                #
                _("Goes to previous visited link."))

        self.inputEventHandlers["goNextVisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goNextVisitedLink,
                # Translators: this is for navigating between links in HTML
                #
                _("Goes to next visited link."))

        self.inputEventHandlers["goPreviousFormFieldHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousFormField,
                # Translators: this is for navigating between form fields in
                # HTML
                #
                _("Goes to previous form field."))

        self.inputEventHandlers["goNextFormFieldHandler"] = \
            input_event.InputEventHandler(
                Script.goNextFormField,
                # Translators: this is for navigating between form fields in
                # HTML
                #
                _("Goes to next form field."))

        self.inputEventHandlers["goPreviousBlockquoteHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousBlockquote,
                # Translators: this is for navigating among blockquotes in
                # HTML
                #
                _("Goes to previous blockquote."))

        self.inputEventHandlers["goNextBlockquoteHandler"] = \
            input_event.InputEventHandler(
                Script.goNextBlockquote,
                # Translators: this is for navigating among blockquotes in
                # HTML
                #
                _("Goes to next blockquote."))

        self.inputEventHandlers["goPreviousTableHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousTable,
                # Translators: this is for navigating between tables in HTML
                #
                _("Goes to previous table."))

        self.inputEventHandlers["goNextTableHandler"] = \
            input_event.InputEventHandler(
                Script.goNextTable,
                # Translators: this is for navigating between tables in HTML
                #
                _("Goes to next table."))

        self.inputEventHandlers["goPreviousLiveRegion"] = \
            input_event.InputEventHandler(
                Script.goPreviousLiveRegion,
                # Translators: this is for navigating between live regions
                #
                _("Goes to previous live region."))

        self.inputEventHandlers["goNextLiveRegion"] = \
            input_event.InputEventHandler(
                Script.goNextLiveRegion,
                # Translators: this is for navigating between live regions
                #
                _("Goes to next live region."))

        self.inputEventHandlers["goLastLiveRegion"] = \
            input_event.InputEventHandler(
                Script.goLastLiveRegion,
                # Translators: this is for navigating to the last live region
                # to make an announcement.
                #
                _("Goes to last live region."))

        self.inputEventHandlers["advanceLivePoliteness"] = \
            input_event.InputEventHandler(
                Script.advanceLivePoliteness,
                # Translators: this is for advancing the live regions 
                # politeness setting
                #
                _("Advance live region politeness setting."))

        self.inputEventHandlers["setLivePolitenessOff"] = \
            input_event.InputEventHandler(
                Script.setLivePolitenessOff,
                # Translators: this is for setting all live regions 
                # to 'off' politeness.
                #
                _("Set default live region politeness level to off."))

        self.inputEventHandlers["monitorLiveRegions"] = \
            input_event.InputEventHandler(
                Script.monitorLiveRegions,
                # Translators: this is a toggle to monitor live regions 
                # or not.
                #
                _("Monitor live regions."))

        self.inputEventHandlers["reviewLiveAnnouncement"] = \
            input_event.InputEventHandler(
                Script.reviewLiveAnnouncement,
                # Translators: this is for reviewing up to nine stored
                # previous live messages.
                #
                _("Review live region announcement."))

        self.inputEventHandlers["goPreviousObjectInOrderHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousObjectInOrder,
                # Translators: this is for navigating between objects
                # (regardless of type) in HTML
                #
                _("Goes to the previous object."))

        self.inputEventHandlers["goNextObjectInOrderHandler"] = \
            input_event.InputEventHandler(
                Script.goNextObjectInOrder,
                # Translators: this is for navigating between objects
                # (regardless of type) in HTML
                #
                _("Goes to the next object."))

        self.inputEventHandlers["toggleCaretNavigationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleCaretNavigation,
                # Translators: Gecko native caret navigation is where
                # Firefox itself controls how the arrow keys move the caret
                # around HTML content.  It's often broken, so Orca needs
                # to provide its own support.  As such, Orca offers the user
                # the ability to switch between the Firefox mode and the
                # Orca mode.
                #
                _("Switches between Gecko native and Orca caret navigation."))

        self.inputEventHandlers["toggleStructuralNavigationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleStructuralNavigation,
                # Translators: the structural navigation keys are designed
                # to move the caret around the HTML content by object type.
                # Thus H moves you to the next heading, Shift H to the
                # previous heading, T to the next table, and so on. Some
                # users prefer to turn this off to use Firefox's search
                # when typing feature.
                #
                _("Toggles structural navigation keys."))

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                # Translators: the Orca "SayAll" command allows the
                # user to press a key and have the entire document in
                # a window be automatically spoken to the user.  If
                # the user presses any key during a SayAll operation,
                # the speech will be interrupted and the cursor will
                # be positioned at the point where the speech was
                # interrupted.
                #
                _("Speaks entire document."))
                
        

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["document:reload"]                        = \
            self.onDocumentReload
        listeners["document:load-complete"]                 = \
            self.onDocumentLoadComplete
        listeners["document:load-stopped"]                  = \
            self.onDocumentLoadStopped
        listeners["object:visible-data-changed"]            = \
            self.onVisibleDataChanged
        listeners["object:state-changed:showing"]           = \
            self.onStateChanged
        listeners["object:state-changed:checked"]           = \
            self.onStateChanged
        listeners["object:state-changed:indeterminate"]     = \
            self.onStateChanged
        listeners["object:state-changed:busy"]              = \
            self.onStateChanged
        listeners["object:children-changed"]                = \
            self.onChildrenChanged
        listeners["object:text-changed:insert"]             = \
            self.onTextInserted

        # [[[TODO: HACK - WDW we need to accomodate Gecko's incorrect
        # use of underscores instead of dashes until they fix their bug.
        # See https://bugzilla.mozilla.org/show_bug.cgi?id=368729]]]
        #
        listeners["object:property-change:accessible_value"] = \
            self.onValueChanged

        return listeners

    def __getArrowBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        arrow keys for navigating HTML content.
        """

        altModMask       =  1 << pyatspi.MODIFIER_ALT
        controlModMask   =  1 << pyatspi.MODIFIER_CONTROL
        shiftAltModMask  = (1 << pyatspi.MODIFIER_SHIFT |
                            1 << pyatspi.MODIFIER_ALT)
        fullModMask      = (1 << pyatspi.MODIFIER_SHIFT |
                            1 << pyatspi.MODIFIER_ALT |
                            1 << pyatspi.MODIFIER_CONTROL |
                            1 << settings.MODIFIER_ORCA)

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                fullModMask,
                0,
                self.inputEventHandlers["goNextCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                fullModMask,
                0,
                self.inputEventHandlers["goPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                fullModMask,
                controlModMask,
                self.inputEventHandlers["goNextWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                fullModMask,
                controlModMask,
                self.inputEventHandlers["goPreviousWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Up",
                fullModMask,
                0,
                self.inputEventHandlers["goPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                fullModMask,
                0,
                self.inputEventHandlers["goNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                fullModMask,
                altModMask,
                self.inputEventHandlers["expandComboBoxHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                fullModMask,
                shiftAltModMask,
                self.inputEventHandlers["goCellRightHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                fullModMask,
                shiftAltModMask,
                self.inputEventHandlers["goCellLeftHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Up",
                fullModMask,
                shiftAltModMask,
                self.inputEventHandlers["goCellUpHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                fullModMask,
                shiftAltModMask,
                self.inputEventHandlers["goCellDownHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Home",
                fullModMask,
                shiftAltModMask,
                self.inputEventHandlers["goCellFirstHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "End",
                fullModMask,
                shiftAltModMask,
                self.inputEventHandlers["goCellLastHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Home",
                fullModMask,
                controlModMask,
                self.inputEventHandlers["goTopOfFileHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "End",
                fullModMask,
                controlModMask,
                self.inputEventHandlers["goBottomOfFileHandler"]))

        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        orcaModMask      =  1 << settings.MODIFIER_ORCA
        shiftModMask     =  1 << pyatspi.MODIFIER_SHIFT
        orcaShiftModMask = (1 << settings.MODIFIER_ORCA |
                            1 << pyatspi.MODIFIER_SHIFT)
        fullModMask      = (1 << pyatspi.MODIFIER_SHIFT |
                            1 << pyatspi.MODIFIER_ALT |
                            1 << pyatspi.MODIFIER_CONTROL |
                            1 << settings.MODIFIER_ORCA)

        keyBindings = default.Script.getKeyBindings(self)

        # NOTE: We include ALT and CONTROL in all the bindings below so as
        # to not conflict with menu and other mnemonics.

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                fullModMask,
                0,
                self.inputEventHandlers["goNextHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "1",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousHeading1Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "1",
                fullModMask,
                0,
                self.inputEventHandlers["goNextHeading1Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "2",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousHeading2Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "2",
                fullModMask,
                0,
                self.inputEventHandlers["goNextHeading2Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "3",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousHeading3Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "3",
                fullModMask,
                0,
                self.inputEventHandlers["goNextHeading3Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "4",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousHeading4Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "4",
                fullModMask,
                0,
                self.inputEventHandlers["goNextHeading4Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "5",
                fullModMask,
                0,
                self.inputEventHandlers["goNextHeading5Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "5",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousHeading5Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "6",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousHeading6Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "6",
                fullModMask,
                0,
                self.inputEventHandlers["goNextHeading6Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousChunkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                fullModMask,
                0,
                self.inputEventHandlers["goNextChunkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousListHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                fullModMask,
                0,
                self.inputEventHandlers["goNextListHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousListItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                fullModMask,
                0,
                self.inputEventHandlers["goNextListItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousUnvisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                fullModMask,
                0,
                self.inputEventHandlers["goNextUnvisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "v",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousVisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "v",
                fullModMask,
                0,
                self.inputEventHandlers["goNextVisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Tab",
                fullModMask,
                orcaShiftModMask,
                self.inputEventHandlers["goPreviousFormFieldHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Tab",
                fullModMask,
                orcaModMask,
                self.inputEventHandlers["goNextFormFieldHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "q",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousBlockquoteHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "q",
                fullModMask,
                0,
                self.inputEventHandlers["goNextBlockquoteHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "t",
                fullModMask,
                shiftModMask,
                self.inputEventHandlers["goPreviousTableHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "t",
                fullModMask,
                0,
                self.inputEventHandlers["goNextTableHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                (1 << pyatspi.MODIFIER_SHIFT \
                 | 1 << pyatspi.MODIFIER_ALT \
                 | 1 << pyatspi.MODIFIER_CONTROL),
                1 << pyatspi.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousLiveRegion"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                (1 << pyatspi.MODIFIER_SHIFT \
                 | 1 << pyatspi.MODIFIER_ALT \
                 | 1 << pyatspi.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextLiveRegion"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "y",
                (1 << pyatspi.MODIFIER_SHIFT \
                 | 1 << pyatspi.MODIFIER_ALT \
                 | 1 << pyatspi.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goLastLiveRegion"]))
                
        # keybindings to provide chat room message history.
        messageKeys = [ "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9" ]
        for messageKey in messageKeys:
            keyBindings.add(
                keybindings.KeyBinding(
                    messageKey,
                    1 << settings.MODIFIER_ORCA,
                    1 << settings.MODIFIER_ORCA,
                    self.inputEventHandlers["reviewLiveAnnouncement"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                (1 << pyatspi.MODIFIER_SHIFT \
                 | 1 << pyatspi.MODIFIER_ALT \
                 | 1 << pyatspi.MODIFIER_CONTROL),
                1 << pyatspi.MODIFIER_SHIFT,
                self.inputEventHandlers["setLivePolitenessOff"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                fullModMask,
                orcaShiftModMask,
                self.inputEventHandlers["monitorLiveRegions"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                (1 << pyatspi.MODIFIER_SHIFT \
                 | 1 << pyatspi.MODIFIER_ALT \
                 | 1 << pyatspi.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["advanceLivePoliteness"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "F12",
                fullModMask,
                orcaModMask,
                self.inputEventHandlers["toggleCaretNavigationHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "SunF37",
                fullModMask,
                orcaModMask,
                self.inputEventHandlers["toggleCaretNavigationHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "z",
                fullModMask,
                orcaModMask,
                self.inputEventHandlers["toggleStructuralNavigationHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                fullModMask,
                orcaModMask,
                self.inputEventHandlers["goNextObjectInOrderHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                fullModMask,
                orcaModMask,
                self.inputEventHandlers["goPreviousObjectInOrderHandler"]))

        if controlCaretNavigation:
            for keyBinding in self.__getArrowBindings().keyBindings:
                keyBindings.add(keyBinding)

        #####################################################################
        #                                                                   #
        #  Unbound handlers                                                 #
        #                                                                   #
        #####################################################################
        keyBindings.add(
            keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["goPreviousLandmark"]))

        keyBindings.add(
             keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["goNextLandmark"]))

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application.
        """

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(12)
        gtk.Widget.show(vbox)

        # General ("Page") Navigation frame.
        #
        generalFrame = gtk.Frame()
        gtk.Widget.show(generalFrame)
        gtk.Box.pack_start(vbox, generalFrame, False, False, 5)

        generalAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(generalAlignment)
        gtk.Container.add(generalFrame, generalAlignment)
        gtk.Alignment.set_padding(generalAlignment, 0, 0, 12, 0)

        generalVBox = gtk.VBox(False, 0)
        gtk.Widget.show(generalVBox)
        gtk.Container.add(generalAlignment, generalVBox)

        # Translators: Gecko native caret navigation is where
        # Firefox itself controls how the arrow keys move the caret
        # around HTML content.  It's often broken, so Orca needs
        # to provide its own support.  As such, Orca offers the user
        # the ability to switch between the Firefox mode and the
        # Orca mode.
        #
        label = _("Use _Orca Caret Navigation")
        self.controlCaretNavigationCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.controlCaretNavigationCheckButton)
        gtk.Box.pack_start(generalVBox,
                           self.controlCaretNavigationCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.controlCaretNavigationCheckButton,
                                    controlCaretNavigation)

        # Translators: Orca provides keystrokes to navigate HTML content
        # in a structural manner: go to previous/next header, list item,
        # table, etc.
        #
        label = _("Use Orca _Structural Navigation")
        self.structuralNavigationCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.structuralNavigationCheckButton)
        gtk.Box.pack_start(generalVBox, self.structuralNavigationCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.structuralNavigationCheckButton,
                                    structuralNavigationEnabled)

        # Translators: when the user arrows up and down in HTML content,
        # it is some times beneficial to always position the cursor at the
        # beginning of the line rather than guessing the position directly
        # above the current cursor position.  This option allows the user
        # to decide the behavior they want.
        #
        label = \
            _("_Position cursor at start of line when navigating vertically")
        self.arrowToLineBeginningCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.arrowToLineBeginningCheckButton)
        gtk.Box.pack_start(generalVBox, self.arrowToLineBeginningCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.arrowToLineBeginningCheckButton,
                                    arrowToLineBeginning)

        # Translators: when the user loads a new page in Firefox, they
        # can optionally tell Orca to automatically start reading a
        # page from beginning to end.
        #
        label = \
            _("Automatically start speaking a page when it is first _loaded")
        self.sayAllOnLoadCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.sayAllOnLoadCheckButton)
        gtk.Box.pack_start(generalVBox, self.sayAllOnLoadCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.sayAllOnLoadCheckButton,
                                    sayAllOnLoad)

        # Translators: this is the title of a panel holding options for
        # how to navigate HTML content (e.g., Orca caret navigation,
        # positioning of caret, etc.).
        #
        generalLabel = gtk.Label("<b>%s</b>" % _("Page Navigation"))
        gtk.Widget.show(generalLabel)
        gtk.Frame.set_label_widget(generalFrame, generalLabel)
        gtk.Label.set_use_markup(generalLabel, True)

        # Table Navigation frame.
        #
        tableFrame = gtk.Frame()
        gtk.Widget.show(tableFrame)
        gtk.Box.pack_start(vbox, tableFrame, False, False, 5)

        tableAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(tableAlignment)
        gtk.Container.add(tableFrame, tableAlignment)
        gtk.Alignment.set_padding(tableAlignment, 0, 0, 12, 0)

        tableVBox = gtk.VBox(False, 0)
        gtk.Widget.show(tableVBox)
        gtk.Container.add(tableAlignment, tableVBox)

        # Translators: this is an option to tell Orca whether or not it
        # should speak table cell coordinates in HTML content.
        #
        label = _("Speak _cell coordinates")
        self.speakCellCoordinatesCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellCoordinatesCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellCoordinatesCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellCoordinatesCheckButton,
                                    speakCellCoordinates)

        # Translators: this is an option to tell Orca whether or not it
        # should speak the span size of a table cell (e.g., how many
        # rows and columns a particular table cell spans in a table).
        #
        label = _("Speak _multiple cell spans")
        self.speakCellSpanCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellSpanCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellSpanCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellSpanCheckButton,
                                    speakCellSpan)

        # Translators: this is an option for whether or not to speak
        # the header of a table cell in HTML content.
        #
        label = _("Announce cell _header")
        self.speakCellHeadersCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellHeadersCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellHeadersCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellHeadersCheckButton,
                                    speakCellHeaders)

        # Translators: this is an option to allow users to skip over
        # empty/blank cells when navigating tables in HTML content.
        #
        label = _("Skip _blank cells")
        self.skipBlankCellsCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.skipBlankCellsCheckButton)
        gtk.Box.pack_start(tableVBox, self.skipBlankCellsCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.skipBlankCellsCheckButton,
                                    skipBlankCells)

        # Translators: this is the title of a panel containing options
        # for specifying how to navigate tables in HTML content.
        #
        tableLabel = gtk.Label("<b>%s</b>" % _("Table Navigation"))
        gtk.Widget.show(tableLabel)
        gtk.Frame.set_label_widget(tableFrame, tableLabel)
        gtk.Label.set_use_markup(tableLabel, True)

        # Find Options frame.
        #
        findFrame = gtk.Frame()
        gtk.Widget.show(findFrame)
        gtk.Box.pack_start(vbox, findFrame, False, False, 5)

        findAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(findAlignment)
        gtk.Container.add(findFrame, findAlignment)
        gtk.Alignment.set_padding(findAlignment, 0, 0, 12, 0)

        findVBox = gtk.VBox(False, 0)
        gtk.Widget.show(findVBox)
        gtk.Container.add(findAlignment, findVBox)

        # Translators: this is an option to allow users to have Orca
        # automatically speak the line that contains the match while
        # the user is still in Firefox's Find toolbar.
        #
        label = _("Speak results during _find")
        self.speakResultsDuringFindCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakResultsDuringFindCheckButton)
        gtk.Box.pack_start(findVBox, self.speakResultsDuringFindCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakResultsDuringFindCheckButton,
                                    speakResultsDuringFind)

        # Translators: this is an option which dictates whether the line
        # that contains the match from the Find toolbar should always
        # be spoken, or only spoken if it is a different line than the
        # line which contained the last match.
        #
        label = _("Onl_y speak changed lines during find")
        self.changedLinesOnlyCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.changedLinesOnlyCheckButton)
        gtk.Box.pack_start(findVBox, self.changedLinesOnlyCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.changedLinesOnlyCheckButton,
                                    onlySpeakChangedLinesDuringFind)

        hbox = gtk.HBox(False, 0)
        gtk.Widget.show(hbox)
        gtk.Box.pack_start(findVBox, hbox, False, False, 0)

        # Translators: this option allows the user to specify the number
        # of matched characters that must be present before Orca speaks
        # the line that contains the results from the Find toolbar.
        #
        self.minimumFindLengthLabel = \
              gtk.Label(_("Minimum length of matched text:"))
        self.minimumFindLengthLabel.set_alignment(0, 0.5)
        gtk.Widget.show(self.minimumFindLengthLabel)
        gtk.Box.pack_start(hbox, self.minimumFindLengthLabel, False, False, 5)

        self.minimumFindLengthAdjustment = \
                       gtk.Adjustment(minimumFindLength, 0, 20, 1)
        self.minimumFindLengthSpinButton = \
                       gtk.SpinButton(self.minimumFindLengthAdjustment, 0.0, 0)
        gtk.Widget.show(self.minimumFindLengthSpinButton)
        gtk.Box.pack_start(hbox, self.minimumFindLengthSpinButton, 
                           False, False, 5)

        acc_targets = []
        acc_src = self.minimumFindLengthLabel.get_accessible()
        relation_set = acc_src.ref_relation_set()
        acc_targ = self.minimumFindLengthSpinButton.get_accessible()
        acc_targets.append(acc_targ)
        relation = atk.Relation(acc_targets, 1)
        relation.set_property('relation-type', atk.RELATION_LABEL_FOR)
        relation_set.add(relation)

        # Translators: this is the title of a panel containing options
        # for using Firefox's Find toolbar.
        #
        findLabel = gtk.Label("<b>%s</b>" % _("Find Options"))
        gtk.Widget.show(findLabel)
        gtk.Frame.set_label_widget(findFrame, findLabel)
        gtk.Label.set_use_markup(findLabel, True)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        global controlCaretNavigation, arrowToLineBeginning, sayAllOnLoad
        global structuralNavigationEnabled
        global speakCellCoordinates, speakCellSpan
        global speakCellHeaders, skipBlankCells
        global speakResultsDuringFind, minimumFindLength
        global onlySpeakChangedLinesDuringFind

        prefs.writelines("\n")

        value = self.controlCaretNavigationCheckButton.get_active()
        prefs.writelines("orca.Gecko.controlCaretNavigation = %s\n" % value)
        controlCaretNavigation = value

        value = self.structuralNavigationCheckButton.get_active()
        prefs.writelines("orca.Gecko.structuralNavigationEnabled = %s\n" % \
                         value)
        structuralNavigationEnabled = value

        value = self.arrowToLineBeginningCheckButton.get_active()
        prefs.writelines("orca.Gecko.arrowToLineBeginning = %s\n" % value)
        arrowToLineBeginning = value

        value = self.sayAllOnLoadCheckButton.get_active()
        prefs.writelines("orca.Gecko.sayAllOnLoad = %s\n" % value)
        sayAllOnLoad = value

        value = self.speakCellCoordinatesCheckButton.get_active()
        prefs.writelines("orca.Gecko.speakCellCoordinates = %s\n" % value)
        speakCellCoordinates = value

        value = self.speakCellSpanCheckButton.get_active()
        prefs.writelines("orca.Gecko.speakCellSpan = %s\n" % value)
        speakCellSpan = value

        value = self.speakCellHeadersCheckButton.get_active()
        prefs.writelines("orca.Gecko.speakCellHeaders = %s\n" % value)
        speakCellHeaders = value

        value = self.skipBlankCellsCheckButton.get_active()
        prefs.writelines("orca.Gecko.skipBlankCells = %s\n" % value)
        skipBlankCells = value

        value = self.speakResultsDuringFindCheckButton.get_active()
        prefs.writelines("orca.Gecko.speakResultsDuringFind = %s\n" % value)
        speakResultsDuringFind = value

        value = self.changedLinesOnlyCheckButton.get_active()
        prefs.writelines("orca.Gecko.onlySpeakChangedLinesDuringFind = %s\n"\
                         % value)
        onlySpeakChangedLinesDuringFind = value

        value = self.minimumFindLengthSpinButton.get_value()
        prefs.writelines("orca.Gecko.minimumFindLength = %s\n" % value)
        minimumFindLength = value

    def getAppState(self):
        """Returns an object that can be passed to setAppState.  This
        object will be use by setAppState to restore any state information
        that was being maintained by the script."""
        return [default.Script.getAppState(self),
                self._documentFrameCaretContext,
                self.lastTableCell]

    def setAppState(self, appState):
        """Sets the application state using the given appState object.

        Arguments:
        - appState: an object obtained from getAppState
        """
        try:
            [defaultAppState,
             self._documentFrameCaretContext,
             self.lastTableCell] = appState
            default.Script.setAppState(self, defaultAppState)
        except:
            debug.printException(debug.LEVEL_WARNING)

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """

        # The reason we override this method is that we only want
        # to consume keystrokes under certain conditions.  For
        # example, we only control the arrow keys when we're
        # managing caret navigation and we're inside document content.
        #
        # [[[TODO: WDW - this might be broken when we're inside a
        # text area that's inside document (or anything else that
        # we want to allow to control its own destiny).]]]

        user_bindings = None
        user_bindings_map = settings.keyBindingsMap
        if user_bindings_map.has_key(self.__module__):
            user_bindings = user_bindings_map[self.__module__]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        consumes = False
        if user_bindings:
            handler = user_bindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                return self.useCaretNavigationModel(keyboardEvent)
            elif handler \
                and handler.function in self._structuralNavigationFunctions:
                return self.useStructuralNavigationModel()
            else:
                consumes = handler != None
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                return self.useCaretNavigationModel(keyboardEvent)
            elif handler \
                and handler.function in self._structuralNavigationFunctions:
                return self.useStructuralNavigationModel()
            else:
                consumes = handler != None
        return consumes

    def textLines(self, obj):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        # Determine the correct "say all by" mode to use.
        #
        sayAllBySentence = \
                      (settings.sayAllStyle == settings.SAYALL_STYLE_SENTENCE)

        [obj, characterOffset] = self.getCaretContext()
        text = self.queryNonEmptyText(obj)
        if text:
            # Attempt to locate the start of the current sentence by
            # searching to the left for a sentence terminator.  If we don't
            # find one, or if the "say all by" mode is not sentence, we'll
            # just start the sayAll from at the beginning of this line/object.
            #
            [line, startOffset, endOffset] = \
                text.getTextAtOffset(
                                 characterOffset,
                                 pyatspi.TEXT_BOUNDARY_LINE_START)
            beginAt = 0
            if line and sayAllBySentence:
                terminators = ['. ', '? ', '! ']
                for terminator in terminators:
                    try:
                        index = line.rindex(terminator,
                                            0,
                                            characterOffset - startOffset)
                        if index > beginAt:
                            beginAt = index
                    except:
                        pass
                characterOffset = startOffset + beginAt

        done = False
        while not done:
            if sayAllBySentence:
                contents = self.getObjectContentsAtOffset(obj, characterOffset)
            else:
                contents = self.getLineContentsAtOffset(obj, characterOffset)
            utterances = self.getUtterancesFromContents(contents)
            clumped = self.clumpUtterances(utterances)
            for i in xrange(len(clumped)):
                [obj, startOffset, endOffset] = \
                                             contents[min(i, len(contents)-1)]
                if obj.getRole() == pyatspi.ROLE_LABEL \
                   and len(obj.getRelationSet()):
                    # This label is labelling something and will be spoken
                    # in conjunction with the object with which it is
                    # associated.
                    #
                    continue
                [string, voice] = clumped[i]
                string = self.adjustForRepeats(string)
                yield [speechserver.SayAllContext(obj, string,
                                                  startOffset, endOffset),
                       voice]

            moreLines = False
            if sayAllBySentence:
                # getObjectContentsAtOffset() gave us all of the descendants
                # of the last object, as long as the last object was not a
                # table.  We need to be sure that we don't "find" one of those
                # children with findNextObject().
                #
                if obj.childCount and obj.getRole() != pyatspi.ROLE_TABLE:
                    obj = obj[obj.childCount - 1]
                while obj and not moreLines:
                    obj = self.findNextObject(obj)
                    if obj:
                        if obj.getRole() in [pyatspi.ROLE_LIST,
                                             pyatspi.ROLE_LIST_ITEM]:
                            # Adjust the offset so that the item number is
                            # spoken.
                            #
                            offset = -1
                        else:
                            offset = 0
                        [obj, characterOffset] = \
                                  self.findFirstCaretContext(obj, offset)
                        moreLines = True
            else:
                [nextObj, nextCharOffset] = self.findNextLine(obj, endOffset-1)
                objExtents = self.getExtents(
                                  obj, characterOffset, characterOffset + 1)
                nextObjExtents = self.getExtents(
                                  nextObj, nextCharOffset, nextCharOffset + 1)
                if not self.onSameLine(objExtents, nextObjExtents):
                    [obj, characterOffset] = nextObj, nextCharOffset
                    moreLines = True

            if not moreLines:
                done = True

    def __sayAllProgressCallback(self, context, callbackType):
        if callbackType == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            #
            # Attempt to keep the content visible on the screen as
            # it is being read, but avoid links as grabFocus sometimes
            # makes them disappear and sayAll to subsequently stop.
            #
            if context.currentOffset == 0 and \
               context.obj.getRole() in [pyatspi.ROLE_HEADING,
                                         pyatspi.ROLE_SECTION,
                                         pyatspi.ROLE_PARAGRAPH]:
                characterCount = context.obj.queryText().characterCount
                self.setCaretPosition(context.obj, characterCount-1)
        elif callbackType == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            try:
                self.setCaretPosition(context.obj, context.currentOffset)
            except:
                characterCount = context.obj.queryText().characterCount
                self.setCaretPosition(context.obj, characterCount-1)
            self.updateBraille(context.obj)
        elif callbackType == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            orca.setLocusOfFocus(None, context.obj, False)
            try:
                self.setCaretPosition(context.obj, context.currentOffset)
            except:
                characterCount = context.obj.queryText().characterCount
                self.setCaretPosition(context.obj, characterCount-1)
            self.updateBraille(context.obj)

    def sayAll(self, inputEvent):
        """Speaks the contents of the document beginning with the present
        location.  Overridden in this script because the sayAll could have
        been started on an object without text (such as an image).
        """

        if not self.inDocumentContent():
            return default.Script.sayAll(self, inputEvent)

        else:
            speech.sayAll(self.textLines(orca_state.locusOfFocus),
                          self.__sayAllProgressCallback)

        return True

    def getDisplayedLabel(self, obj):
        """If there is an object labelling the given object, return the
        text being displayed for the object labelling this object.
        Otherwise, return None.  Overridden here to handle instances
        of bogus labels and form fields where a lack of labels necessitates
        our attempt to guess the text that is functioning as a label.

        Argument:
        - obj: the object in question

        Returns the string of the object labelling this object, or None
        if there is nothing of interest here.
        """

        string = None
        labels = self.findDisplayedLabel(obj)
        for label in labels:
            # Check to see if the official labels are valid.
            #
            bogus = False
            if self.inDocumentContent() \
               and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                     pyatspi.ROLE_LIST]:
                # Bogus case #1:
                # <label></label> surrounding the entire combo box/list which
                # makes the entire combo box's/list's contents serve as the
                # label. We can identify this case because the child of the
                # label is the combo box/list. See bug #428114, #441476.
                #
                if label.childCount:
                    bogus = (label[0].getRole() == obj.getRole())

            if not bogus:
                # Bogus case #2:
                # <label></label> surrounds not just the text serving as the
                # label, but whitespace characters as well (e.g. the text
                # serving as the label is on its own line within the HTML).
                # Because of the Mozilla whitespace bug, these characters
                # will become part of the label which will cause the label
                # and name to no longer match and Orca to seemingly repeat
                # the label.  Therefore, strip out surrounding whitespace.
                # See bug #441610 and
                # https://bugzilla.mozilla.org/show_bug.cgi?id=348901
                #
                string = self.appendString(string, self.expandEOCs(label))

        return string

    def onCaretMoved(self, event):
        """Caret movement in Gecko is somewhat unreliable and
        unpredictable, but we need to handle it.  When we detect caret
        movement, we make sure we update our own notion of the caret
        position: our caretContext is an [obj, characterOffset] that
        points to our current item and character (if applicable) of
        interest.  If our current item doesn't implement the
        accessible text specialization, the characterOffset value
        is meaningless (and typically -1)."""

        # We now get caret-moved events for items that do not have
        # focus.  This will enable us to provide better support for
        # the use of the Find toolbar.  It also means that we need
        # to check the event.source before assuming that we should
        # update our position, set the locus of focus, etc.
        #
        # Possibility #1: A form control is given focus and a non-
        # focusable item (the form itself, a table cell within the
        # form, etc.) issues the event.  These should be ignored
        # UNLESS focus was moved from a form field  to non-focusable
        # text in the document frame via mouse click.
        #
        if not event.source.getState().contains(pyatspi.STATE_FOCUSABLE) \
           and self.isFormField(orca_state.locusOfFocus) \
           and not isinstance(orca_state.lastInputEvent,
                              input_event.MouseButtonEvent):
            return

        # Possibility #2: We're looking at the Help contents.  As
        # the selected item changes in the list on the left, we're
        # getting caret-moved events for the changing content on
        # the right.  We want to update the caret context but not
        # the locus of focus.
        #
        if orca_state.locusOfFocus \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_LIST_ITEM \
           and not self.inDocumentContent(orca_state.locusOfFocus) \
           and self.inDocumentContent(event.source):
            self.setCaretContext(event.source, event.detail1)
            return

        # Possibility #3: We're using the Find toolbar.  In this case
        # we want to update the caret context.  If the user has opted
        # to have results spoken during the find (i.e., while still
        # in the Find toolbar), speak the line containing the caret
        # based on the user-customizable settings.
        #
        if orca_state.locusOfFocus \
           and orca_state.locusOfFocus.getRole() in [pyatspi.ROLE_ENTRY,
                                                pyatspi.ROLE_PUSH_BUTTON] \
           and orca_state.locusOfFocus.parent.getRole() == \
                                            pyatspi.ROLE_TOOL_BAR \
           and self.inDocumentContent(event.source):
            [obj, offset] = self.getCaretContext()
            self.setCaretContext(event.source, event.detail1)

            origExtents = self.getExtents(obj, offset - 1, offset)
            newExtents = self.getExtents(event.source,
                                         event.detail1 - 1,
                                         event.detail1)
            text = self.queryNonEmptyText(event.source)
            if speakResultsDuringFind and text:
                nSelections = text.getNSelections()
                if nSelections:
                    [start, end] = text.getSelection(0)
                    enoughSelected = (end - start) >= minimumFindLength
                    lineChanged = not self.onSameLine(origExtents, newExtents)

                    # If the user starts backspacing over the text in the
                    # toolbar entry, he/she is indicating they want to perform
                    # a different search. Because madeFindAnnounement may
                    # be set to True, we should reset it -- but only if we
                    # detect the line has also changed.  We're not getting
                    # events from the Find entry, so we have to compare
                    # offsets.
                    #
                    if (obj == event.source) and (offset > event.detail1) \
                        and lineChanged:
                        self.madeFindAnnouncement = False

                    if enoughSelected:
                        if lineChanged or not self.madeFindAnnouncement or \
                           not onlySpeakChangedLinesDuringFind:
                            line = self.getLineContentsAtOffset(event.source,
                                                                event.detail1)
                            self.speakContents(line)
                            self.madeFindAnnouncement = True

            return

        # Possibility #4: We called grabFocus() on this item because it has
        # the overflow:auto; style associated with it.  We need to ignore
        # this event.  See bug #471537.  But we don't want to do this for
        # entries.  See bug #501447.
        #
        if self.isSameObject(event.source, self._objectForFocusGrab) \
           and event.source.getRole() != pyatspi.ROLE_ENTRY:
            self._objectForFocusGrab = None
            return

        # Possibility #5: Orca is controlling the caret, we just left an
        # entry, and text was inserted into that entry via javascript as
        # a result of it losing focus.  This is a bogus event, but a fix
        # might not make it into Firefox 3.  :-(  See GNOME bug 472345
        # as well as https://bugzilla.mozilla.org/show_bug.cgi?id=394493.
        #
        if event.source \
           and event.source.getRole() == pyatspi.ROLE_ENTRY \
           and event.source.getState().contains(pyatspi.STATE_FOCUSABLE) \
           and not event.source.getState().contains( \
                                           pyatspi.STATE_FOCUSED):
            return

        # Possibility #6: We are looking at an ARIA widget where the user
        # has traversed the widget (eg. tree) with the arrows.  We are getting
        # an extra caret-moved event in these situations. See bug #471878 and
        # Mozilla bug #394318.
        #
        if self.isAriaWidget(event.source) \
                and isinstance(orca_state.lastInputEvent,
                           input_event.KeyboardEvent) \
                and orca_state.lastInputEvent.event_string in \
                                              ["Up", "Down", "Left", "Right"] \
                and orca_state.locusOfFocus.getRole() != pyatspi.ROLE_ENTRY:
            return

        # If Orca is controlling the caret and we just moved to a line that
        # begins with a link, and that link begins on the previous line,
        # we need to ignore this event. Otherwise our caret context will
        # become the beginning of the link on the previous line.
        #
        if orca_state.locusOfFocus \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_LINK \
           and self.isSameObject(orca_state.locusOfFocus.parent, event.source):
            offset = self.getCharacterOffsetInParent(orca_state.locusOfFocus)
            if offset == event.detail1:
                return

        # If Orca is controlling the caret, it is possible to arrow into
        # a menu item inside of a combo box.  This is something that is
        # not possible in Firefox caret browsing mode and seems to confuse
        # Firefox sufficiently that it wants to generate a caret-moved
        # event for *something*:  might be the menu item, might be a nearby
        # link, might be something else.  If it's the menu item, we double
        # speak it.  If it's something else, we don't want the locusOfFocus
        # to be set there.  So for now, let's just ignore these.
        #
        if orca_state.locusOfFocus \
            and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_MENU_ITEM \
            and self.inDocumentContent(event.source):
            return

        # If {overflow:hidden} is in the document's style sheet, we seem
        # to get an additional item in the hierarchy:  An object of role
        # ROLE_UNKNOWN which is the single child of the document frame and
        # contains all the items which we'd expect to find in the document
        # frame.  Under these conditions, we will get a caret-moved event
        # for the document frame with detail1 == 0 after a focus: event for
        # the object.  We need to ignore both of these events else we will
        # jump to the top of the document.
        #
        # http://bugzilla.gnome.org/show_bug.cgi?id=412677
        # https://bugzilla.mozilla.org/show_bug.cgi?id=371955
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME \
           and event.source.childCount \
           and event.source[0].getRole() == pyatspi.ROLE_UNKNOWN:
            return

        # Otherwise, we'll just assume that the thing in which the caret
        # moved is the locus of focus.  We'll only do this if the current
        # object that's the locus of focus no longer has focus, though.
        # The reason for this is that we can indeed get caret-moved events
        # from things that really have nothing to do with the locus of
        # focus.
        #
        if orca_state.locusOfFocus \
            and not orca_state.locusOfFocus.getState().contains(
                        pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source, False)

        # We need to handle HTML content differently because we do our
        # own navigation and we also handle the
        # EMBEDDED_OBJECT_CHARACTER.  If we're not in HTML content,
        # we'll defer to the default script.  If we are in HTML
        # content, we'll figure out where we are and then defer to the
        # default script.  It will typically end up calling some of
        # our other overidden methods (e.g., sayCharacter, sayWord,
        # sayLine, etc.).
        #
        if not self.inDocumentContent():
            default.Script.onCaretMoved(self, event)
            return

        text = self.queryNonEmptyText(event.source)

        #print "HERE: caretContext=", self.getCaretContext()
        #print "            source=", event.source
        #print "       caretOffset=", text.caretOffset
        #print "    characterCount=", text.characterCount

        [obj, characterOffset] = \
            self.findFirstCaretContext(event.source,
                                       text.caretOffset)
        self.setCaretContext(obj, characterOffset)

        #print "       ended up at=", self.getCaretContext()

        # If the user presses left or right, we'll set the target
        # column for up/down navigation by line.  The goal here is
        # to make sure the caret moves somewhat vertically when
        # going up/down by line versus jumping to the beginning of
        # the line.  Note that whether we actually attempt to do
        # this is handled by the value of the global
        # arrowToLineBeginning.
        #
        if isinstance(orca_state.lastInputEvent,
                      input_event.KeyboardEvent):
            string = orca_state.lastNonModifierKeyEvent.event_string
            if (string == "Left") or (string == "Right"):
                [obj, characterOffset] = self.getCaretContext()
                self.targetCharacterExtents = \
                    self.getExtents(obj,
                                    characterOffset,
                                    characterOffset + 1)

        # If the last event was a mouse event, then just return. This
        # prevents the multiple utterances of text selected via the mouse
        # (see bug #409728).
        #
        if isinstance(orca_state.lastInputEvent,
                      input_event.MouseButtonEvent):
            return                

        default.Script.onCaretMoved(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an an object.

        Arguments:
        - event: the Event
        """

        self._destroyLineCache()

        # The search entries in Firefox's and Thunderbird's top toolbars
        # contain text which functions as the label (Yahoo, Entire Message)
        # and which gets deleted just prior to the entry gaining focus.  If
        # we pass that event on to the default script, it will set the
        # entry to the locus of focus silently and then the focus event
        # will not cause the entry to be spoken.  In addition, if the
        # Location autocomplete is expanded and Backspace is pressed,
        # the locus of focus will be a table cell and the default script
        # will not speak the characters being deleted from the entry.
        #
        if event.source and orca_state.locusOfFocus \
           and not self.isSameObject(event.source, orca_state.locusOfFocus):
            toolbar = self.getAncestor(event.source,
                                       [pyatspi.ROLE_TOOL_BAR],
                                       [pyatspi.ROLE_DOCUMENT_FRAME])
            if toolbar:
                if orca_state.locusOfFocus.getRole() == pyatspi.ROLE_TABLE_CELL:
                    orca.setLocusOfFocus(event, event.source, False)
                else:
                    return

        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        self._destroyLineCache()

        # handle live region events
        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

        default.Script.onTextInserted(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed.  In particular, we are looking
        for addition events often associated with Javascipt insertion.  One such
        such example would be the programmatic insertion of a tooltip or alert  
        dialog."""
        # no need moving forward if we don't have our target.
        if event.any_data is None:
            return

        # handle live region events
        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

    def onDocumentReload(self, event):
        """Called when the reload button is hit for a web page."""
        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = True

    def onDocumentLoadComplete(self, event):
        """Called when a web page load is completed."""
        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            # Reset the live region manager.
            self.liveMngr.reset()
            self._loadingDocumentContent = False

    def onDocumentLoadStopped(self, event):
        """Called when a web page load is interrupted."""
        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = False

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """
        if event.source.getRole() == pyatspi.ROLE_FRAME:
            self.liveMngr.flushMessages()

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """
        # If this event is the result of our calling grabFocus() on
        # this object in setCaretPosition(), we want to ignore it.
        # See bug #471537.  But we don't want to do this for entries.
        # See bug #501447.
        #
        if self.isSameObject(event.source, self._objectForFocusGrab) \
           and event.source.getRole() != pyatspi.ROLE_ENTRY:
            orca.setLocusOfFocus(event, event.source, False)
            return
            
        # We're going to ignore focus events on the frame.  They
        # are often intermingled with menu activity, wreaking havoc
        # on the context.
        #
        if (event.source.getRole() == pyatspi.ROLE_FRAME) \
           or (not event.source.getRole()):
            return

        # If {overflow:hidden} is in the document's style sheet, we seem
        # to get an additional item in the hierarchy:  An object of role
        # ROLE_UNKNOWN which is the single child of the document frame and
        # contains all the items which we'd expect to find in the document
        # frame.  Under these conditions, we will get a caret-moved event
        # for the document frame with detail1 == 0 after a focus: event for
        # the object.  We need to ignore both of these events else we will
        # jump to the top of the document.
        #
        # http://bugzilla.gnome.org/show_bug.cgi?id=412677
        # https://bugzilla.mozilla.org/show_bug.cgi?id=371955
        #
        if event.source.getRole() == pyatspi.ROLE_UNKNOWN:
            return

        # We also ignore focus events on the panel that holds the document
        # frame.  We end up getting these typically because we've called
        # grabFocus on this panel when we're doing caret navigation.  In
        # those cases, we want the locus of focus to be the subcomponent
        # that really holds the caret.
        #
        if event.source.getRole() == pyatspi.ROLE_PANEL:
            documentFrame = self.getDocumentFrame()
            if documentFrame and (documentFrame.parent == event.source):
                return
            else:
                # Web pages can contain their own panels.  If the locus
                # of focus is within that panel, we probably moved off
                # of a focusable item (like a link within the panel)
                # to something non-focusable (like text within the panel).
                # If we don't ignore this event, we'll loop to the top
                # of the panel.
                #
                containingPanel = \
                            self.getAncestor(orca_state.locusOfFocus,
                                             [pyatspi.ROLE_PANEL],
                                             [pyatspi.ROLE_DOCUMENT_FRAME])
                if self.isSameObject(containingPanel, event.source):
                    return

        # When we get a focus event on the document frame, it's usually
        # because we did a grabFocus on its parent in setCaretPosition.
        # We try to handle this here by seeing if there is already a
        # caret context for the document frame.  If we succeed, then
        # we set the focus on the object that's holding the caret.
        #
        if event.source \
            and (event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME):
            try:
                [obj, characterOffset] = self.getCaretContext()
                if not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                    orca.setLocusOfFocus(event, obj)
                    return
            except:
                pass

        # We're also going to ignore menus that are children of menu
        # bars.  They never really get focus themselves - it's always
        # a transient event and one of the menu items or submenus will
        # get focus immediately after the menu gets focus.  So...we
        # compress the events.
        #
        # [[[WDW - commented this out on 27-Jul-2006 based upon feedback
        # from Lynn Monsanto that it was getting in the way for Firefox
        # and Yelp.]]]
        #
        #if (event.source.getRole() == pyatspi.ROLE_MENU) \
        #   and event.source.parent \
        #   and (event.source.parent.getRole() == pyatspi.ROLE_MENU_BAR):
        #    return

        # Autocomplete widgets are a complex beast as well.  When they
        # get focus, their child (which is an entry) really has focus.
        # Their child also issues a focus: event, so we just ignore
        # the autocomplete focus: event.
        #
        if event.source.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            # [[[WDW - we used to force the locus of focus to the
            # entry.  The idea was that even if the entry issued
            # a focus: event, the locus of focus would not change.
            # The problem, however, is that Gecko often gives us
            # a *different* child whenever we ask for the entry.
            # So...we end up just depending upon the entry to issue
            # us a focus: event.  The focus: event usually
            # occurs immediately after the autocomplete gets
            # focus.]]]
            #
            #entry = self.getAutocompleteEntry(event.source)
            #orca.setLocusOfFocus(event, entry)
            return

        # If a link gets focus, it might be a link that contains just an
        # image, as we often see in web pages.  In these cases, we give
        # the image focus and announce it.
        #
        if event.source.getRole() == pyatspi.ROLE_LINK:
            containingLink = self.getAncestor(orca_state.locusOfFocus,
                                              [pyatspi.ROLE_LINK],
                                              [pyatspi.ROLE_DOCUMENT_FRAME])
            if containingLink == event.source:
                return
            elif event.source.childCount == 1:
                child = event.source[0]
                orca.setLocusOfFocus(event, child)
                return

        default.Script.onFocus(self, event)

    def onLinkSelected(self, event):
        """Called when a link gets selected.  Note that in Firefox 3,
        link selected events are not issued when a link is selected.
        Instead, a focus: event is issued.  This is 'old' code left
        over from Yelp and Firefox 2.

        Arguments:
        - event: the Event
        """

        text = self.queryNonEmptyText(event.source)
        hypertext = event.source.queryHypertext()
        linkIndex = self.getLinkIndex(event.source, text.caretOffset)

        if linkIndex >= 0:
            link = hypertext.getLink(linkIndex)
            linkText = text.getText(link.startIndex, link.endIndex)
            #[string, startOffset, endOffset] = text.getTextAtOffset(
            #    text.caretOffset,
            #    pyatspi.TEXT_BOUNDARY_LINE_START)
            #print "onLinkSelected", event.source.getRole() , string,
            #print "  caretOffset:     ", text.caretOffset
            #print "  line startOffset:", startOffset
            #print "  line endOffset:  ", startOffset
            #print "  caret in line:   ", text.caretOffset - startOffset
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        elif text:
            # We'll just assume the whole thing is a link.  This happens
            # in yelp when we navigate the table of contents of something
            # like the Desktop Accessibility Guide.
            #
            linkText = text.getText(0, -1)
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        else:
            speech.speak(rolenames.getSpeechForRoleName(event.source),
                         self.voices[settings.HYPERLINK_VOICE])

        self.updateBraille(event.source)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # HTML radio buttons don't automatically become selected when
        # they receive focus.  The user has to press the space bar on
        # them much like checkboxes.  But if the user clicks on the
        # radio button with the mouse, we'll wind up speaking the
        # state twice because of the focus event.
        #
        if event.type.startswith("object:state-changed:checked") \
           and event.source \
           and (event.source.getRole() == pyatspi.ROLE_RADIO_BUTTON) \
           and (event.detail1 == 1) \
           and self.inDocumentContent(event.source) \
           and not self.isAriaWidget(event.source) \
           and not isinstance(orca_state.lastInputEvent,
                              input_event.MouseButtonEvent):
            orca.visualAppearanceChanged(event, event.source)
            return

        # If an autocomplete appears beneath an entry, we don't want
        # to prevent the user from being able to arrow into it.
        #
        if event.type.startswith("object:state-changed:showing") \
           and event.source \
           and (event.source.getRole() == pyatspi.ROLE_WINDOW) \
           and orca_state.locusOfFocus:
            if orca_state.locusOfFocus.getRole() in [pyatspi.ROLE_ENTRY,
                                                     pyatspi.ROLE_LIST_ITEM]:
                self._autocompleteVisible = event.detail1
            
        # We care when the document frame changes it's busy state.  That
        # means it has started/stopped loading content.
        #
        if event.type.startswith("object:state-changed:busy"):
            if event.source \
                and (event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME):
                finishedLoading = False
                if orca_state.locusOfFocus \
                    and (orca_state.locusOfFocus.getRole() \
                         == pyatspi.ROLE_LIST_ITEM) \
                   and not self.inDocumentContent(orca_state.locusOfFocus):
                    # The event is for the changing contents of the help
                    # frame as the user navigates from topic to topic in
                    # the list on the left.  Ignore this.
                    #
                    return

                elif event.detail1:
                    # A detail1=1 means the page has started loading.
                    #
                    self._loadingDocumentContent = True

                    # Translators: this is in reference to loading a web page.
                    #
                    message = _("Loading.  Please wait.")

                elif event.source.name:
                    # Translators: this is in reference to loading a web page.
                    #
                    message = _("Finished loading %s.") % event.source.name
                    finishedLoading = True

                else:
                    # Translators: this is in reference to loading a web page.
                    #
                    message = _("Finished loading.")
                    finishedLoading = True

                braille.displayMessage(message)
                speech.stop()
                speech.speak(message)

                if finishedLoading:
                    # We first try to figure out where the caret is on
                    # the newly loaded page.  If it is on an editable
                    # object (e.g., a text entry), then we present just
                    # that object.  Otherwise, we force the caret to the
                    # top of the page and start a SayAll from that position.
                    #
                    [obj, characterOffset] = self.getCaretContext()
                    atTop = False
                    if not obj:
                        self.clearCaretContext()
                        [obj, characterOffset] = self.getCaretContext()
                        atTop = True

                    # If we found nothing, then don't do anything.  Otherwise
                    # determine if we should do a SayAll or not.
                    #
                    if not obj:
                        return
                    elif not atTop \
                        and not obj.getState().contains(\
                            pyatspi.STATE_EDITABLE):
                        self.clearCaretContext()
                        [obj, characterOffset] = self.getCaretContext()
                        if not obj:
                            return

                    # When a document is loaded, we are going to
                    # assume that the newly loaded document frame has
                    # focus.  Gecko doesn't seem to give us a focus
                    # event for this, though, so we will force the
                    # locus of focus here.
                    #
                    orca.setLocusOfFocus(event, obj, False)
                    self.setCaretPosition(obj, characterOffset)

                    # For braille, we just show the current line
                    # containing the caret.  For speech, however, we
                    # will start a Say All operation if the caret is
                    # in an uneditable area (e.g., it's not in a text
                    # entry area such as Google's search text entry).
                    # Otherwise, we'll just speak the line that the
                    # caret is on.
                    #
                    self.updateBraille(obj)

                    if obj.getState().contains(pyatspi.STATE_EDITABLE):
                        speech.speakUtterances(\
                            self.speechGenerator.getSpeech(obj, True))
                    elif not sayAllOnLoad:
                        self.speakContents(\
                            self.getLineContentsAtOffset(obj,
                                                         characterOffset))
                    elif settings.enableSpeech:
                        self.sayAll(None)

            return

        default.Script.onStateChanged(self, event)

    def onVisibleDataChanged(self, event):
        """Called when the visible data of an object changes.
        We do this to detect when the user switches between
        the tabs holding different URL pages in the Firefox
        window."""

        # See if we have a frame who has a document frame.
        #
        documentFrame = None
        if (event.source.getRole() == pyatspi.ROLE_FRAME) \
            and event.source.getState().contains(pyatspi.STATE_ACTIVE):

            documentFrame = self.getDocumentFrame()

            # If the document frame is busy loading, we won't present
            # anything to prevent Orca from being too chatty.  We also
            # don't want to present anything if we're not in the document.
            #
            if self._loadingDocumentContent or not self.inDocumentContent():
                return

            braille.displayMessage(documentFrame.name)
            speech.stop()
            speech.speak(
                "%s %s" \
                % (documentFrame.name,
                   rolenames.rolenames[pyatspi.ROLE_PAGE_TAB].speech))

            [obj, characterOffset] = self.getCaretContext()
            if not obj:
                [obj, characterOffset] = self.findNextCaretInOrder()
                self.setCaretContext(obj, characterOffset)
            if not obj:
                return

            # When a document tab is tabbed to, we will just present the
            # line where the caret currently is.
            #
            self.presentLine(obj, characterOffset)

    def handleProgressBarUpdate(self, event, obj):
        """Determine whether this progress bar event should be spoken or not.
        For Firefox, we don't want to speak the small "page load" progress
        bar. All other Firefox progress bars get passed onto the parent 
        class for handling.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj:  the Accessible progress bar object.
        """

        rolesList = [pyatspi.ROLE_PROGRESS_BAR, \
                     pyatspi.ROLE_STATUS_BAR, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if not self.isDesiredFocusedItem(event.source, rolesList):
            default.Script.handleProgressBarUpdate(self, event, obj)

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

        if (obj.getRole() == pyatspi.ROLE_CHECK_BOX) \
            and obj.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, obj, False)

        default.Script.visualAppearanceChanged(self, event, obj)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
        # Sometimes we get different accessibles for the same object.
        #
        if self.isSameObject(oldLocusOfFocus, newLocusOfFocus):
            return

        # Try to handle the case where a spurious focus event was tossed
        # at us.
        #
        if newLocusOfFocus and self.inDocumentContent(newLocusOfFocus):
            text = self.queryNonEmptyText(newLocusOfFocus)
            if text:
                caretOffset = text.caretOffset

                # If the old locusOfFocus was not in the document frame, and
                # if the old locusOfFocus's frame is the same as the frame
                # containing the new locusOfFocus, we likely just returned
                # from a toolbar (find, location, menu bar, etc.).  We do
                # not want to speak the hierarchy between that toolbar and
                # the document frame.
                #
                if oldLocusOfFocus and \
                   not self.inDocumentContent(oldLocusOfFocus):
                    oldFrame = self.getFrame(oldLocusOfFocus)
                    newFrame = self.getFrame(newLocusOfFocus)
                    if self.isSameObject(oldFrame, newFrame) or \
                           newLocusOfFocus.getRole() == pyatspi.ROLE_DIALOG:
                        self.setCaretPosition(newLocusOfFocus, caretOffset)
                        self.presentLine(newLocusOfFocus, caretOffset)
                        return

            else:
                caretOffset = 0
            [obj, characterOffset] = \
                  self.findFirstCaretContext(newLocusOfFocus, caretOffset)
            self.setCaretContext(obj, characterOffset)

        # If we've just landed in the Find toolbar, reset
        # self.madeFindAnnouncement.
        #
        if newLocusOfFocus and \
           newLocusOfFocus.getRole() == pyatspi.ROLE_ENTRY and \
           newLocusOfFocus.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            self.madeFindAnnouncement = False

        # We'll ignore focus changes when the document frame is busy.
        # This will keep Orca from chatting too much while a page is
        # loading.
        #
        if event:
            inDialog = self.getAncestor(event.source,
                                        [pyatspi.ROLE_DIALOG],
                                        [pyatspi.ROLE_DOCUMENT_FRAME])
            if not inDialog:
                inDialog = self.getAncestor(event.source,
                                            [pyatspi.ROLE_ALERT],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])

        if self._loadingDocumentContent \
           and event and event.source \
           and not event.source.getRole() in [pyatspi.ROLE_DIALOG,
                                              pyatspi.ROLE_ALERT] \
           and not inDialog:
            return

        # Don't bother speaking all the information about the HTML
        # container - it's duplicated all over the place.  So, we
        # just speak the role.
        #
        if newLocusOfFocus \
           and newLocusOfFocus.getRole() == pyatspi.ROLE_HTML_CONTAINER:
            # We always automatically go back to focus tracking mode when
            # the focus changes.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()
            self.updateBraille(newLocusOfFocus)
            speech.speak(rolenames.getSpeechForRoleName(newLocusOfFocus))
            return

        # [[[TODO: WDW - I commented this out because we all of a sudden
        # started losing the presentation of links when we tabbed to them
        # sometime around 21-Dec-2006.  It was a hack to begin with, so
        # it might be something to completely remove at some time in the
        # future.]]]
        #
        #elif newLocusOfFocus \
        #    and newLocusOfFocus.getRole() == pyatspi.ROLE_LINK:
        #    # Gecko issues focus: events for a link when you move the
        #    # caret to or tab to a link.  By the time we've gotten here,
        #    # though, we've already presented the link via a caret moved
        #    # event or some other event.  So...we don't anything.
        #    #
        #    try:
        #        [obj, characterOffset] = self.getCaretContext()
        #        if newLocusOfFocus == obj:
        #            return
        #    except:
        #        pass
        default.Script.locusOfFocusChanged(self,
                                           event,
                                           oldLocusOfFocus,
                                           newLocusOfFocus)

    def findObjectOnLine(self, obj, offset, contents):
        """Determines if the item described by the object and offset is
        in the line contents.

        Arguments:
        - obj: the Accessible
        - offset: the character offset within obj
        - contents: a list of (obj, startOffset, endOffset) tuples

        Returns the index of the item if found; -1 if not found.
        """

        if not obj or not contents or not len(contents):
            return -1

        index = -1
        for content in contents:
            [candidate, start, end] = content

            # When we get the line contents, we include a focusable list
            # as a list because that is what we want to present.  However,
            # when we set the caret context, we set it to the position
            # (and object) that immediately precedes it.  Therefore, that's
            # what we need to look at when trying to determine our position.
            #
            if candidate.getRole() == pyatspi.ROLE_LIST \
               and candidate.getState().contains(pyatspi.STATE_FOCUSABLE):
                start = self.getCharacterOffsetInParent(candidate)
                end = start + 1
                candidate = candidate.parent

            if self.isSameObject(obj, candidate) \
               and start <= offset <= end:
                index = contents.index(content)
                break

        return index

    def _updateLineCache(self, obj, offset):
        """Tries to intelligently update our stored lines. Destroying them if
        need be.

        Arguments:
        - obj: the Accessible
        - offset: the character offset within obj
        """

        index = self.findObjectOnLine(obj, offset, self._currentLineContents)
        if index < 0:
            index = self.findObjectOnLine(obj, 
                                          offset, 
                                          self._previousLineContents)
            if index >= 0:
                self._nextLineContents = self._currentLineContents
                self._currentLineContents = self._previousLineContents
                self._previousLineContents = None
            else:
                index = self.findObjectOnLine(obj, 
                                              offset, 
                                              self._nextLineContents)
                if index >= 0:
                    self._previousLineContents = self._currentLineContents
                    self._currentLineContents = self._nextLineContents
                    self._nextLineContents = None
                else:
                    self._destroyLineCache()

    def _destroyLineCache(self):
        """Removes all of the stored lines."""

        self._previousLineContents = None
        self._currentLineContents = None
        self._nextLineContents = None

    def presentLine(self, obj, offset):
        """Presents the current line in speech and in braille.

        Arguments:
        - obj: the Accessible at the caret
        - offset: the offset within obj
        """

        contents = self._currentLineContents
        index = self.findObjectOnLine(obj, offset, contents)
        if index < 0:
            self._currentLineContents = self.getLineContentsAtOffset(obj,
                                                                     offset)
        self.speakContents(self._currentLineContents)
        self.updateBraille(obj)

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the given object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not self.inDocumentContent():
            default.Script.updateBraille(self, obj, extraRegion)
            return

        if not obj:
            return

        braille.clear()
        line = braille.Line()
        braille.addLine(line)

        # Some text areas have a character offset of -1 when you tab
        # into them.  In these cases, they show all the text as being
        # selected.  We don't know quite what to do in that case,
        # so we'll just pretend the caret is at the beginning (0).
        #
        [focusedObj, focusedCharacterOffset] = self.getCaretContext()

        # [[[TODO: HACK - WDW when composing e-mail in Thunderbird and
        # when entering text in editable text areas, Gecko likes to
        # force the last character of a line to be a newline.  So,
        # we adjust for this because we want to keep meaningful text
        # on the display.]]]
        #
        needToRefresh = False
        lineContentsOffset = focusedCharacterOffset
        focusedObjText = self.queryNonEmptyText(focusedObj)
        if focusedObjText:
            char = focusedObjText.getText(focusedCharacterOffset,
                                          focusedCharacterOffset + 1)
            if char == "\n":
                lineContentsOffset = max(0, focusedCharacterOffset - 1)
                needToRefresh = True

        contents = self._currentLineContents
        index = self.findObjectOnLine(focusedObj, 
                                      max(0, lineContentsOffset),
                                      contents)
        if index < 0 or needToRefresh:
            contents = self.getLineContentsAtOffset(focusedObj,
                                                    max(0, lineContentsOffset))
            self._currentLineContents = contents

        if not len(contents):
            return

        focusedRegion = None
        for content in contents:
            [obj, startOffset, endOffset] = content
            if not obj:
                continue

            # If this is a label that's labelling something else, we'll
            # get the label via a braille generator. [[[TODO: WDW - this is
            # all to hack around the way checkboxes and their labels
            # are handled in document content.  For now, we will display
            # the label so we can track the caret in it on the braille
            # display.  So...we'll comment this section out.]]]
            #
            #if self.isLabellingContents(obj, contents):
            #    continue

            # Treat the focused combo box and its selected menu item
            # as the same object for the purposes of displaying the
            # item in braille.
            #
            if focusedObj.getRole() == pyatspi.ROLE_COMBO_BOX \
               and obj.getRole() == pyatspi.ROLE_MENU_ITEM:
                comboBox = self.getAncestor(obj,
                                            [pyatspi.ROLE_COMBO_BOX],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])
                isFocusedObj = self.isSameObject(comboBox, focusedObj)
            else:
                isFocusedObj = self.isSameObject(obj, focusedObj)

            text = self.queryNonEmptyText(obj)
            if not self.isNavigableAria(obj):
                # Treat unnavigable ARIA widgets like normal default.py widgets
                #
                [regions, fRegion] = \
                          self.brailleGenerator.getBrailleRegions(obj)
                if isFocusedObj:
                    focusedRegion = fRegion
            elif obj.getRole() in [pyatspi.ROLE_ENTRY,
                                   pyatspi.ROLE_PASSWORD_TEXT] \
                or ((obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME) \
                    and obj.getState().contains(pyatspi.STATE_EDITABLE)):
                label = self.getDisplayedLabel(obj)
                regions = [braille.Text(obj, label, " $l")]
                if isFocusedObj:
                    focusedRegion = regions[0]
            elif text and (obj.getRole() != pyatspi.ROLE_MENU_ITEM):
                string = text.getText(startOffset, endOffset)
                regions = [braille.Region(
                    string,
                    focusedCharacterOffset - startOffset)]
                if obj.getRole() == pyatspi.ROLE_LINK:
                    link = obj
                else:
                    link = self.getAncestor(obj,
                                            [pyatspi.ROLE_LINK],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])
                if link:
                    regions.append(braille.Region(
                        " " + rolenames.getBrailleForRoleName(link)))

                if isFocusedObj \
                   and (focusedCharacterOffset >= startOffset) \
                   and (focusedCharacterOffset < endOffset):
                    focusedRegion = regions[0]

            elif self.isLayoutOnly(obj):
                continue
            else:
                [regions, fRegion] = \
                          self.brailleGenerator.getBrailleRegions(obj)
                if isFocusedObj:
                    focusedRegion = fRegion

            # We only want to display the heading role and level if we
            # have found the final item in that heading, or if that
            # heading contains no children.
            #
            containingHeading = \
                self.getAncestor(obj,
                                 [pyatspi.ROLE_HEADING],
                                 [pyatspi.ROLE_DOCUMENT_FRAME])
            isLastObject = contents.index(content) == (len(contents) - 1)
            if obj.getRole() == pyatspi.ROLE_HEADING:
                appendRole = isLastObject or not obj.childCount
            elif containingHeading and isLastObject:
                obj = containingHeading
                appendRole = True

            if obj.getRole() == pyatspi.ROLE_HEADING and appendRole:
                level = self.getHeadingLevel(obj)
                # Translators: the 'h' below represents a heading level
                # attribute for content that you might find in something
                # such as HTML content (e.g., <h1>). The translated form
                # is meant to be a single character followed by a numeric
                # heading level, where the single character is to indicate
                # 'heading'.
                #
                regions.append(braille.Region(" " + _("h%d" % level)))

            if len(line.regions):
                line.addRegion(braille.Region(" "))

            line.addRegions(regions)

            # If we're inside of a combo box, we only want to display
            # the selected menu item.
            #
            if obj.getRole() == pyatspi.ROLE_MENU_ITEM \
               and obj.getState().contains(pyatspi.STATE_FOCUSED):
                break

        if extraRegion:
            line.addRegion(extraRegion)

        braille.setFocus(focusedRegion)
        braille.refresh(True)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #

        if not self.inDocumentContent():
            default.Script.sayCharacter(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        text = self.queryNonEmptyText(obj)
        if text:
            # If the caret is at the end of text and we're not in an
            # entry, something bad is going on, so decrement the offset
            # before speaking the character.
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string) and \
               obj.getRole() != pyatspi.ROLE_ENTRY:
                print "YIKES in Gecko.sayCharacter!"
                characterOffset -= 1

        self.speakCharacterAtOffset(obj, characterOffset)

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent():
            default.Script.sayWord(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        text = self.queryNonEmptyText(obj)
        if text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the previous word.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next word via
            # a call to goNextWord.]]]
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string):
                print "YIKES in Gecko.sayWord!"
                characterOffset -= 1

        # Ideally in an entry we would just let default.sayWord() handle
        # things.  That fails to work when navigating backwords by word.
        # Because getUtterancesFromContents() now uses the speechgenerator
        # with entries, we need to handle word navigation in entries here.
        #
        wordContents = self.getWordContentsAtOffset(obj, characterOffset)
        if obj.getRole() != pyatspi.ROLE_ENTRY:
            self.speakContents(wordContents)
        else:
            [textObj, startOffset, endOffset] = wordContents[0]
            word = textObj.queryText().getText(startOffset, endOffset)
            speech.speakUtterances([word], self.getACSS(textObj, word))

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent() or \
           obj.getRole() == pyatspi.ROLE_ENTRY:
            default.Script.sayLine(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        text = self.queryNonEmptyText(obj)
        if text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the current line.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next line via
            # a call to goNextLine.]]]
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string):
                print "YIKES in Gecko.sayLine!"
                characterOffset -= 1

        self.speakContents(self.getLineContentsAtOffset(obj, characterOffset))

    ####################################################################
    #                                                                  #
    # Methods for debugging.                                           #
    #                                                                  #
    ####################################################################

    def outlineExtents(self, obj, startOffset, endOffset):
        """Draws an outline around the given text for the object or the entire
        object if it has no text.  This is for debug purposes only.

        Arguments:
        -obj: the object
        -startOffset: character offset to start at
        -endOffset: character offset just after last character to end at
        """
        [x, y, width, height] = self.getExtents(obj, startOffset, endOffset)
        self.drawOutline(x, y, width, height)

    def dumpInfo(self, obj):
        """Dumps the parental hierachy info of obj to stdout."""

        if obj.parent:
            self.dumpInfo(obj.parent)

        print "---"
        text = self.queryNonEmptyText(obj)
        if text and obj.getRole() != pyatspi.ROLE_DOCUMENT_FRAME:
            string = text.getText(0, -1)
        else:
            string = ""
        print obj, obj.name, obj.getRole(), \
              obj.accessible.getIndexInParent(), string
        offset = self.getCharacterOffsetInParent(obj)
        if offset >= 0:
            print "  offset =", offset

    def getDocumentContents(self):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the current caret context (or the beginning of the document if
        there is no caret context).

        WARNING: THIS TRAVERSES A LARGE PART OF THE DOCUMENT AND IS
        INTENDED PRIMARILY FOR DEBUGGING PURPOSES ONLY."""

        contents = []
        lastObj = None
        lastExtents = None
        self.clearCaretContext()
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            if True or obj.getState().contains(pyatspi.STATE_SHOWING):
                if self.queryNonEmptyText(obj):
                    # Check for text being on a different line.  Gecko
                    # gives us odd character extents sometimes, so we
                    # defensively ignore those.
                    #
                    characterExtents = self.getExtents(
                        obj, characterOffset, characterOffset + 1)
                    if characterExtents != (0, 0, 0, 0):
                        if lastExtents \
                           and not self.onSameLine(lastExtents,
                                                   characterExtents):
                            contents.append([None, -1, -1])
                            lastExtents = characterExtents

                    # Check to see if we've moved across objects or are
                    # still on the same object.  If we've moved, we want
                    # to add another context.  If we're still on the same
                    # object, we just want to update the end offset.
                    #
                    if (len(contents) == 0) or (obj != lastObj):
                        contents.append([obj,
                                         characterOffset,
                                         characterOffset + 1])
                    else:
                        [currentObj, startOffset, endOffset] = contents[-1]
                        if characterOffset == endOffset:
                            contents[-1] = [currentObj,    # obj
                                            startOffset,   # startOffset
                                            endOffset + 1] # endOffset
                        else:
                            contents.append([obj,
                                             characterOffset,
                                             characterOffset + 1])
                else:
                    # Some objects present text and/or something visual
                    # (e.g., a checkbox), so we want to track it.
                    #
                    contents.append([obj, -1, -1])

                lastObj = obj

            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)

        return contents

    def getDocumentString(self):
        """Trivial debug utility to stringify the document contents
        showing on the screen."""

        contents = ""
        lastObj = None
        lastCharacterExtents = None
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            if obj and obj.getState().contains(pyatspi.STATE_SHOWING):
                characterExtents = self.getExtents(
                    obj, characterOffset, characterOffset + 1)
                if lastObj and (lastObj != obj):
                    if obj.getRole() == pyatspi.ROLE_LIST_ITEM:
                        contents += "\n"
                    if lastObj.getRole() == pyatspi.ROLE_LINK:
                        contents += ">"
                    elif (lastCharacterExtents[1] < characterExtents[1]):
                        contents += "\n"
                    elif obj.getRole() == pyatspi.ROLE_TABLE_CELL:
                        parent = obj.parent
                        index = obj.getIndexInParent()
                        if parent.queryTable().getColumnAtIndex(index) != 0:
                            contents += " "
                    elif obj.getRole() == pyatspi.ROLE_LINK:
                        contents += "<"
                contents += self.getCharacterAtOffset(obj, characterOffset)
                lastObj = obj
                lastCharacterExtents = characterExtents
            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)
        if lastObj and lastObj.getRole() == pyatspi.ROLE_LINK:
            contents += ">"
        return contents

    def dumpContents(self, inputEvent, contents=None):
        """Dumps the document frame content to stdout.

        Arguments:
        -inputEvent: the input event that caused this to be called
        -contents: an ordered list of [obj, startOffset, endOffset] tuples
        """
        if not contents:
            contents = self.getDocumentContents()
        string = ""
        extents = None
        for content in contents:
            [obj, startOffset, endOffset] = content
            if obj:
                extents = self.getBoundary(
                    self.getExtents(obj, startOffset, endOffset),
                    extents)
                text = self.queryNonEmptyText(obj)
                if text:
                    string += "[%s] text='%s' " % (obj.getRole(),
                                                   text.getText(startOffset,
                                                                endOffset))
                else:
                    string += "[%s] name='%s' " % (obj.getRole(), obj.name)
            else:
                string += "\nNEWLINE\n"
        print "==========================="
        print string
        self.drawOutline(extents[0], extents[1], extents[2], extents[3])

    ####################################################################
    #                                                                  #
    # Utility Methods                                                  #
    #                                                                  #
    ####################################################################

    def queryNonEmptyText(self, obj):
        """Get the text interface associated with an object, if it is
        non-empty.

        Arguments:
        - obj: an accessible object
        """

        try:
            text = obj.queryText()
        except:
            pass
        else:
            if text.characterCount:
                return text

        return None

    def inDocumentContent(self, obj=None):
        """Returns True if the given object (defaults to the current
        locus of focus is in the document content).
        """
        if not obj:
            obj = orca_state.locusOfFocus

        while obj:
            role = obj.getRole()
            if role == pyatspi.ROLE_DOCUMENT_FRAME \
                    or role == pyatspi.ROLE_EMBEDDED:
                return True
            else:
                obj = obj.parent
        return False

    def getDocumentFrame(self):
        """Returns the document frame that holds the content being shown."""

        # [[[TODO: WDW - this is based upon the 12-Oct-2006 implementation
        # that uses the EMBEDS relation on the top level frame as a means
        # to find the document frame.  Future implementations will break
        # this.]]]
        #
        documentFrame = None
        for child in self.app:
            if child.getRole() == pyatspi.ROLE_FRAME:
                relationSet = child.getRelationSet()
                for relation in relationSet:
                    if relation.getRelationType()  \
                        == pyatspi.RELATION_EMBEDS:
                        documentFrame = relation.getTarget(0)
                        if documentFrame.getState().contains( \
                            pyatspi.STATE_SHOWING):
                            break
                        else:
                            documentFrame = None

        return documentFrame
                        
    def getURI(self, obj):
        """Return the URI for a given link object.

        Arguments:
        - obj: the Accessible object.
        """
        # Getting a link's URI requires a little workaround due to  
        # https://bugzilla.mozilla.org/show_bug.cgi?id=379747.  You should be
        # able to use getURI() directly on the link but instead must use
        # ihypertext.getLink(0) on parent then use getURI on returned 
        # ihyperlink.
        try:
            ihyperlink = obj.parent.queryHypertext().getLink(0)
        except:
            return None
        else:
            return ihyperlink.getURI(0)
    
    def getDocumentFrameURI(self):
        """Returns the URI of the document frame that is active."""
        try:
            documentFrame = self.getDocumentFrame()
        except AttributeError:
            return None
        attrs = documentFrame.queryDocument().getAttributes()
        for attr in attrs:
            if attr.startswith('DocURL'):
                return attr[7:]
        return None

    def getUnicodeText(self, obj):
        """Returns the unicode text for an object or None if the object
        doesn't implement the accessible text specialization.
        """

        text = self.queryNonEmptyText(obj)
        if text:
            unicodeText = text.getText(0, -1).decode("UTF-8")
        else:
            unicodeText = None
        return unicodeText

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if we should do our own caret navigation.
        """

        if not controlCaretNavigation:
            return False

        if not self.inDocumentContent():
            return False

        if not self.isNavigableAria(orca_state.locusOfFocus):
            return False

        weHandleIt = True
        obj = orca_state.locusOfFocus
        if obj and (obj.getRole() == pyatspi.ROLE_ENTRY):
            text        = obj.queryText()
            length      = text.characterCount
            caretOffset = text.caretOffset
            singleLine  = obj.getState().contains(
                pyatspi.STATE_SINGLE_LINE)

            # Single line entries have an additional newline character
            # at the end.
            #
            newLineAdjustment = int(not singleLine)

            # We want to use our caret navigation model in an entry if
            # there's nothing in the entry, we're at the beginning of
            # the entry and press Left or Up, or we're at the end of the
            # entry and press Right or Down.
            #
            if length == 0 \
               or ((length == 1) and (text.getText(0, -1) == "\n")):
                weHandleIt = True
            elif caretOffset <= 0:
                weHandleIt = keyboardEvent.event_string \
                             in ["Up", "Left"]
            elif caretOffset >= length - newLineAdjustment \
                 and not self._autocompleteVisible:
                weHandleIt = keyboardEvent.event_string \
                             in ["Down", "Right"]
            else:
                weHandleIt = False

            if singleLine and not weHandleIt \
               and not self._autocompleteVisible:
                weHandleIt = keyboardEvent.event_string in ["Up", "Down"]

        elif keyboardEvent.modifiers & (1 << pyatspi.MODIFIER_ALT):
            # Alt+Down Arrow is the Firefox command to expand/collapse the
            # *currently focused* combo box.  When Orca is controlling the
            # caret, it is possible to navigate into a combo box *without
            # giving focus to that combo box*.  Under these circumstances,
            # the menu item has focus.  Because the user knows that he/she
            # is on a combo box, he/she expects to be able to use Alt+Down
            # Arrow to expand the combo box.  Therefore, if a menu item has
            # focus and Alt+Down Arrow is pressed, we will handle it by
            # giving the combo box focus and expanding it as the user
            # expects.  We also want to avoid grabbing focus on a combo box.
            # Therefore, if the caret is immediately before a combo box,
            # we'll hand it the same way.
            #
            if keyboardEvent.event_string == "Down":
                [obj, offset] = self.getCaretContext()
                index = self.getChildIndex(obj, offset)
                if index >= 0:
                    weHandleIt = \
                        obj[index].getRole() == pyatspi.ROLE_COMBO_BOX
                if not weHandleIt:
                    weHandleIt = obj.getRole() == pyatspi.ROLE_MENU_ITEM

        elif obj and (obj.getRole() == pyatspi.ROLE_COMBO_BOX):
            # We'll let Firefox handle the navigation of combo boxes.
            #
            weHandleIt = keyboardEvent.event_string in ["Left", "Right"]

        elif obj and (obj.getRole() in [pyatspi.ROLE_MENU_ITEM,
                                        pyatspi.ROLE_LIST_ITEM]):
            # We'll let Firefox handle the navigation of combo boxes and
            # lists in forms.
            #
            weHandleIt = not obj.getState().contains(pyatspi.STATE_FOCUSED)

        elif obj and (obj.getRole() == pyatspi.ROLE_LIST):
            # We'll let Firefox handle the navigation of lists in forms.
            #
            weHandleIt = not obj.getState().contains(pyatspi.STATE_FOCUSABLE)

        return weHandleIt

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation.
        [[[TODO: WDW - this should return False if we're in something
        like an entry area or a list because we want their keyboard
        navigation stuff to work.]]]
        """

        letThemDoItEditableRoles = [pyatspi.ROLE_ENTRY,
                                    pyatspi.ROLE_TEXT,
                                    pyatspi.ROLE_PASSWORD_TEXT]
        letThemDoItSelectionRoles = [pyatspi.ROLE_LIST,
                                     pyatspi.ROLE_LIST_ITEM,
                                     pyatspi.ROLE_MENU_ITEM]

        if not structuralNavigationEnabled:
            return False

        if not self.isNavigableAria(orca_state.locusOfFocus):
            return False

        # If the Orca_Modifier key was pressed, we're handling it.
        #
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            mods = orca_state.lastInputEvent.modifiers
            isOrcaKey = mods & (1 << settings.MODIFIER_ORCA)
            if isOrcaKey:
                return True

        obj = orca_state.locusOfFocus
        while obj:
            if obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
                # Don't use the structural navivation model if the
                # user is editing the document.
                return not obj.getState().contains(pyatspi.STATE_EDITABLE)
            elif obj.getRole() in letThemDoItEditableRoles:
                return not obj.getState().contains(pyatspi.STATE_EDITABLE)
            elif obj.getRole() in letThemDoItSelectionRoles:
                return not obj.getState().contains(pyatspi.STATE_FOCUSED)
            elif obj.getRole() == pyatspi.ROLE_COMBO_BOX:
                return False
            else:
                obj = obj.parent

        return False

    def isNavigableAria(self, obj):
        """Returns True if the object being examined is an ARIA widget where
           we want to provide Orca keyboard navigation.  Returning False
           indicates that we want Firefox to handle key commands.
        """
        attrs = self._getAttrDictionary(orca_state.locusOfFocus)
        try:
            # ARIA landmark widgets
            if attrs['xml-roles'] in ARIA_LANDMARKS:
                return True
            # ARIA live region
            elif attrs.has_key('container-live'):
                return True
            # All other ARIA widgets
            else:
                return False
        except (KeyError, TypeError):
            return True

    def isAriaWidget(self, obj=None):
        """Returns True if the object being examined is an ARIA widget.

        Arguments:
        - obj: The accessible object of interest.  If None, the
        locusOfFocus is examined.
        """
        obj = obj or orca_state.locusOfFocus
        attrs = self._getAttrDictionary(obj)
        return (attrs.has_key('xml-roles') and not attrs.has_key('live'))

    def _getAttrDictionary(self, obj):
        return dict([attr.split(':', 1) for attr in obj.getAttributes()])

    def isAriaAlert(self, obj):
        """Returns True if the given object is an ARIA wairole:alert or 
           wairole:tooltip.
        """
        if obj is None:
            return False
        attrs = obj.getAttributes()
        if attrs is None:
            return False
        for attr in attrs:
            if attr == 'xml-roles:alert' or attr == 'xml-roles:tooltip':
                return True
        return False

    def handleAsLiveRegion(self, event):
        """Returns True if the given event (object:children-changed, object:
        text-insert only) should be considered a live region event"""

        # We will try to eliminate objects that cannot be considered live
        # regions.  We will handle everything else as a live region.  We
        # will do the cheap tests first
        if self._loadingDocumentContent \
              or not  settings.inferLiveRegions \
              or not event.type.endswith(':system'):
            return False

        # Ideally, we would like to do a inDocumentContent() call to filter out
        # events that are not in the document.  Unfortunately, this is an 
        # expensive call.  Instead we will do some heuristics to filter out
        # chrome events with the least amount of IPC as possible.

        # event.type specific checks
        if event.type.startswith('object:children-changed'):
            # This will filter out lists that are not of interest and
            # events from other tabs.
            stateset = event.source.getState()
            if stateset.contains(pyatspi.STATE_FOCUSABLE) \
                   or stateset.contains(pyatspi.STATE_FOCUSED) \
                   or not stateset.contains(pyatspi.STATE_VISIBLE):
                return False

            # Now we need to look at the object attributes
            attrs = self._getAttrDictionary(event.source)
            # Good live region markup
            if attrs.has_key('container-live'):
                return True

            # We see this one with the URL bar opening (sometimes)
            if attrs.has_key('tag') and attrs['tag'] == 'xul:richlistbox':
                return False

            # This eliminates all ARIA widgets that are not considered live
            if attrs.has_key('xml-roles') \
                                    and not attrs.has_key('container-live'):
                return False

        else: # object:text-inserted event
            # Live regions will not be focusable.
            # Filter out events from hidden tabs (not VISIBLE)
            stateset = event.source.getState()
            if stateset.contains(pyatspi.STATE_FOCUSABLE) \
                   or stateset.contains(pyatspi.STATE_FOCUSED) \
                   or not stateset.contains(pyatspi.STATE_VISIBLE):
                return False

            attrs = self._getAttrDictionary(event.source)
            # Good live region markup
            if attrs.has_key('container-live'):
                return True

            # This might be too restrictive but we need it to filter
            # out URLs that are displayed when the location list opens.
            if attrs.has_key('tag') \
                    and attrs['tag'] == 'xul:description' \
                    or attrs['tag'] == 'xul:label':
                return False

            # This eliminates all ARIA widgets that are not considered live
            if attrs.has_key('xml-roles') \
                                and not attrs.has_key('container-live'):
                return False
        # It sure looks like a live region
        return True

    def getCharacterOffsetInParent(self, obj):
        """Returns the character offset of the embedded object
        character for this object in its parent's accessible text.

        Arguments:
        - obj: an Accessible that should implement the accessible hyperlink
               specialization.

        Returns an integer representing the character offset of the
        embedded object character for this hyperlink in its parent's
        accessible text, or -1 something was amuck.
        """

        try:
            hyperlink = obj.queryHyperlink()
        except NotImplementedError:
            offset = -1
        else:
            offset = hyperlink.startIndex

        return offset

    def getChildIndex(self, obj, characterOffset):
        """Given an object that implements accessible text, determine
        the index of the child that is represented by an
        EMBEDDED_OBJECT_CHARACTER at characterOffset in the object's
        accessible text."""

        try:
            hypertext = obj.queryHypertext()
        except NotImplementedError:
            index = -1
        else:
            index = hypertext.getLinkIndex(characterOffset)

        return index

    def getExtents(self, obj, startOffset, endOffset):
        """Returns [x, y, width, height] of the text at the given offsets
        if the object implements accessible text, or just the extents of
        the object if it doesn't implement accessible text.
        """
        if not obj:
            return [0, 0, 0, 0]

        # The menu items that are children of combo boxes have unique
        # extents based on their physical position, even though they are
        # not showing.  Therefore, if the object in question is a menu
        # item, get the object extents rather than the range extents for
        # the text. Similarly, if it's a menu in a combo box, get the
        # extents of the combo box.
        #
        text = self.queryNonEmptyText(obj)
        if text and obj.getRole() != pyatspi.ROLE_MENU_ITEM:
            extents = text.getRangeExtents(startOffset, endOffset, 0)
        elif obj.getRole() == pyatspi.ROLE_MENU \
             and obj.parent.getRole() == pyatspi.ROLE_COMBO_BOX:
            ext = obj.parent.queryComponent().getExtents(0)
            extents = [ext.x, ext.y, ext.width, ext.height]
        else:
            ext = obj.queryComponent().getExtents(0)
            extents = [ext.x, ext.y, ext.width, ext.height]
        return extents

    def getBoundary(self, a, b):
        """Returns the smallest [x, y, width, height] that encompasses
        both extents a and b.

        Arguments:
        -a: [x, y, width, height]
        -b: [x, y, width, height]
        """
        if not a:
            return b
        if not b:
            return a
        smallestX1 = min(a[0], b[0])
        smallestY1 = min(a[1], b[1])
        largestX2  = max(a[0] + a[2], b[0] + b[2])
        largestY2  = max(a[1] + a[3], b[1] + b[3])
        return [smallestX1,
                smallestY1,
                largestX2 - smallestX1,
                largestY2 - smallestY1]

    def onSameLine(self, a, b, pixelDelta=5):
        """Determine if extents a and b are on the same line.

        Arguments:
        -a: [x, y, width, height]
        -b: [x, y, width, height]

        Returns True if a and b are on the same line.
        """

        # If a and b are identical, by definition they are on the same line.
        #
        if a == b:
            return True

        # For now, we'll just take a look at the bottom of the area.
        # The code after this takes the whole extents into account,
        # but that logic has issues in the case where we have
        # something very tall next to lots of shorter lines (e.g., an
        # image with lots of text to the left or right of it.  The
        # number 11 here represents something that seems to work well
        # with superscripts and subscripts on a line as well as pages
        # with smaller fonts on them, such as craig's list.
        #
        if abs(a[1] - b[1]) > 11:
            return False

        # If there's an overlap of 1 pixel or less, they are on different
        # lines.  Keep in mind "lowest" and "highest" mean visually on the
        # screen, but that the value is the y coordinate.
        #
        highestBottom = min(a[1] + a[3], b[1] + b[3])
        lowestTop     = max(a[1],        b[1])
        if lowestTop >= highestBottom - 1:
            return False

        return True

        # If we do overlap, lets see how much.  We'll require a 25% overlap
        # for now...
        #
        #if lowestTop < highestBottom:
        #    overlapAmount = highestBottom - lowestTop
        #    shortestHeight = min(a[3], b[3])
        #    return ((1.0 * overlapAmount) / shortestHeight) > 0.25
        #else:
        #    return False

    def isLabellingContents(self, obj, contents):
        """Given and obj and a list of [obj, startOffset, endOffset] tuples,
        determine if obj is labelling anything in the tuples.

        Returns the object being labelled, or None.
        """

        if obj.getRole() != pyatspi.ROLE_LABEL:
            return None

        relationSet = obj.getRelationSet()
        if not relationSet:
            return None

        for relation in relationSet:
            if relation.getRelationType() \
                == pyatspi.RELATION_LABEL_FOR:
                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    for content in contents:
                        if content[0] == target:
                            return target

        return None

    def getAutocompleteEntry(self, obj):
        """Returns the ROLE_ENTRY object of a ROLE_AUTOCOMPLETE object or
        None if the entry cannot be found.
        """

        for child in obj:
            if child and (child.getRole() == pyatspi.ROLE_ENTRY):
                return child

        return None

    def getCellCoordinates(self, obj):
        """Returns the [row, col] of a ROLE_TABLE_CELL or [0, 0]
        if the coordinates cannot be found.
        """

        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE_CELL],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])

        parent = obj.parent
        try:
            table = parent.queryTable()
        except:
            pass
        else:
            row = table.getRowAtIndex(obj.getIndexInParent())
            col = table.getColumnAtIndex(obj.getIndexInParent())
            return [row, col]

        return [0, 0]

    def isSameCell(self, obj, coordinates1, coordinates2):
        """Returns True if coordinates1 and coordinates2 refer to the
        same cell in the specified table.

        Arguments:
        - obj: the table in which to compare the coordinates
        - coordinates1: [row, col]
        - coordinates2: [row, col]
        """

        try:
            table = obj.queryTable()
        except:
            pass
        else:
            index1 = table.getIndexAt(coordinates1[0], coordinates1[1])
            index2 = table.getIndexAt(coordinates2[0], coordinates2[1])
            return (index1 == index2)

        return False

    def isBlankCell(self, obj):
        """Returns True if the table cell is empty or consists of a single
        non-breaking space.

        Arguments:
        - obj: the table cell to examime
        """

        text = self.getDisplayedText(obj)
        if text and text != u'\u00A0':
            return False
        else:
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LINK:
                    return False

            return True

    def isNonUniformTable(self, obj):
        """Returns True if the obj is a non-uniform table (i.e. a table
        where at least one cell spans multiple rows and/or columns).

        Arguments:
        - obj: the table to examine
        """

        try:
            table = obj.queryTable()
        except:
            pass
        else:
            for i in xrange(obj.childCount):
                [isCell, row, col, rowExtents, colExtents, isSelected] = \
                                       table.getRowColumnExtentsAtIndex(i)
                if (rowExtents > 1) or (colExtents > 1):
                    return True

        return False

    def isHeader(self, obj):
        """Returns True if the table cell is a header"""

        if not obj:
            return False

        attributes = obj.getAttributes()
        if attributes:
            for attribute in attributes:
                if attribute == "tag:TH":
                    return True

        return False

    def isInHeaderRow(self, obj):
        """Returns True if all of the cells in the same row as this cell are
        headers.

        Arguments:
        - obj: the table cell whose row is to be examined
        """

        if obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            table = obj.parent.queryTable()
            row = table.getRowAtIndex(obj.getIndexInParent())
            for col in xrange(table.nColumns):
                cell = table.getAccessibleAt(row, col)
                if not self.isHeader(cell):
                    return False

        return True

    def isInHeaderColumn(self, obj):
        """Returns True if all of the cells in the same column as this cell
        are headers.

        Arguments:
        - obj: the table cell whose column is to be examined
        """

        if obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            table = obj.parent.queryTable()
            col = table.getColumnAtIndex(obj.getIndexInParent())
            for row in xrange(table.nRows):
                cell = table.getAccessibleAt(row, col)
                if not self.isHeader(cell):
                    return False

        return True

    def getRowHeaders(self, obj):
        """Returns a list of table cells that serve as a row header for
        the specified TABLE_CELL.
        """

        rowHeaders = []
        if not obj:
            return rowHeaders

        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            [row, col] = self.getCellCoordinates(obj)
            # Theoretically, we should be able to quickly get the text
            # of a {row, column}Header via get{Row,Column}Description().
            # Mozilla doesn't expose the information that way, however.
            # get{Row, Column}Header seems to work sometimes.
            #
            header = table.getRowHeader(row)
            if header:
                rowHeaders.append(header)

            # Headers that are strictly marked up with <th> do not seem
            # to be exposed through get{Row, Column}Header.
            #
            else:
                # If our cell spans multiple rows, we want to get all of
                # the headers that apply.
                #
                rowspan = table.getRowExtentAt(row, col)
                for r in range(row, row+rowspan):
                    # We could have multiple headers for a given row, one
                    # header per column.  Presumably all of the headers are
                    # prior to our present location.
                    #
                    for c in range(0, col):
                        cell = table.getAccessibleAt(r, c)
                        text = self.queryNonEmptyText(cell)
                        if self.isHeader(cell) and text \
                           and not cell in rowHeaders:
                            rowHeaders.append(cell)

        return rowHeaders

    def getColumnHeaders(self, obj):
        """Returns a list of table cells that serve as a column header for
        the specified TABLE_CELL.
        """

        columnHeaders = []
        if not obj:
            return columnHeaders

        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            [row, col] = self.getCellCoordinates(obj)
            # Theoretically, we should be able to quickly get the text
            # of a {row, column}Header via get{Row,Column}Description().
            # Mozilla doesn't expose the information that way, however.
            # get{Row, Column}Header seems to work sometimes.
            #
            header = table.getColumnHeader(col)
            if header:
                columnHeaders.append(header)

            # Headers that are strictly marked up with <th> do not seem
            # to be exposed through get{Row, Column}Header.
            #
            else:
                # If our cell spans multiple columns, we want to get all of
                # the headers that apply.
                #
                colspan = table.getColumnExtentAt(row, col)
                for c in range(col, col+colspan):
                    # We could have multiple headers for a given column, one
                    # header per row.  Presumably all of the headers are
                    # prior to our present location.
                    #
                    for r in range(0, row):
                        cell = table.getAccessibleAt(r, c)
                        text = self.queryNonEmptyText(cell)
                        if self.isHeader(cell) and text \
                           and not cell in columnHeaders:
                            columnHeaders.append(cell)

        return columnHeaders

    def getCellSpanInfo(self, obj):
        """Returns a string reflecting the number of rows and/or columns
        spanned by a table cell when multiple rows and/or columns are spanned.
        """

        if not obj or (obj.getRole() != pyatspi.ROLE_TABLE_CELL):
            return

        [row, col] = self.getCellCoordinates(obj)
        table = obj.parent.queryTable()
        rowspan = table.getRowExtentAt(row, col)
        colspan = table.getColumnExtentAt(row, col)
        spanString = None
        if (colspan > 1) and (rowspan > 1):
            # Translators: The cell here refers to a cell within an HTML
            # table.  We need to announce when the cell occupies or "spans"
            # more than a single row and/or column.
            #
            spanString = _("Cell spans %d rows and %d columns") % \
                          (rowspan, colspan)
        elif (colspan > 1):
            # Translators: The cell here refers to a cell within an HTML
            # table.  We need to announce when the cell occupies or "spans"
            # more than a single row and/or column.
            #
            spanString = _("Cell spans %d columns") % colspan
        elif (rowspan > 1):
            # Translators: The cell here refers to a cell within an HTML
            # table.  We need to announce when the cell occupies or "spans"
            # more than a single row and/or column.
            #
            spanString = _("Cell spans %d rows") % rowspan

        return spanString

    def getTableCaption(self, obj):
        """Returns the ROLE_CAPTION object of a ROLE_TABLE object or None
        if the caption cannot be found.
        """

        for child in obj:
            if child and (child.getRole() == pyatspi.ROLE_CAPTION):
                return child

        return None

    def getLinkBasename(self, obj):
        """Returns the relevant information from the URI.  The idea is
        to attempt to strip off all prefix and suffix, much like the
        basename command in a shell."""

        basename = None

        try:
            hyperlink = obj.queryHyperlink()
        except:
            pass
        else:
            uri = hyperlink.getURI(0)
            if uri and len(uri):
                # Get the last thing after all the /'s, unless it ends
                # in a /.  If it ends in a /, we'll look to the stuff
                # before the ending /.
                #
                if uri[-1] == "/":
                    basename = uri[0:-1]
                    basename = basename.split('/')[-1]
                else:
                    basename = uri.split('/')[-1]
                    if basename.startswith("index"):
                        basename = uri.split('/')[-2]

                    # Now, try to strip off the suffixes.
                    #
                    basename = basename.split('.')[0]
                    basename = basename.split('?')[0]
                    basename = basename.split('#')[0]

        return basename

    def isFormField(self, obj):
        """Returns True if the given object is a field inside of a form."""

        containingForm = self.getAncestor(obj,
                                          [pyatspi.ROLE_FORM],
                                          [pyatspi.ROLE_DOCUMENT_FRAME])
        isField = containingForm \
                  and not obj.getRole() in [pyatspi.ROLE_LINK,
                                            pyatspi.ROLE_MENU_ITEM,
                                            pyatspi.ROLE_LIST_ITEM,
                                            pyatspi.ROLE_UNKNOWN] \
                  and obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
                  and obj.getState().contains(pyatspi.STATE_SENSITIVE)

        return isField

    def isBlockquote(self, obj):
        """Returns True if the object is a blockquote"""

        if not obj:
            return False

        attributes = obj.getAttributes()
        if attributes:
            for attribute in attributes:
                if attribute == "tag:BLOCKQUOTE":
                    return True

        return False

    def isUselessObject(self, obj):
        """Returns true if the given object is an obj that doesn't
        have any meaning associated with it and it is not inside a
        link."""

        if not obj:
            return True

        useless = False

        textObj = self.queryNonEmptyText(obj)
        if not textObj and obj.getRole() == pyatspi.ROLE_PARAGRAPH:
            useless = True
        elif obj.getRole() in [pyatspi.ROLE_IMAGE, \
                               pyatspi.ROLE_TABLE_CELL, \
                               pyatspi.ROLE_SECTION]:
            text = self.getDisplayedText(obj)
            if (not text) or (len(text) == 0):
                text = self.getDisplayedLabel(obj)
                if (not text) or (len(text) == 0):
                    useless = True

        if useless:
            link = self.getAncestor(obj,
                                    [pyatspi.ROLE_LINK],
                                    [pyatspi.ROLE_DOCUMENT_FRAME])
            if link:
                useless = False

        return useless

    def isLayoutOnly(self, obj):
        """Returns True if the given object is for layout purposes only."""

        if self.isUselessObject(obj):
            debug.println(debug.LEVEL_FINEST,
                          "Object deemed to be useless: %s" % obj)
            return True

        else:
            return default.Script.isLayoutOnly(self, obj)

    def pursueForFlatReview(self, obj):
        """Determines if we should look any further at the object
        for flat review."""

        # [[[TODO: HACK - WDW Gecko has issues about the SHOWING
        # state of objects, especially those in document frames.
        # It tells us the content in tabs that are not showing
        # is actually showing.  See:
        #
        # http://bugzilla.gnome.org/show_bug.cgi?id=408071
        #
        # To work around this, we do a little extra check.  If
        # the obj is a document, and it's not the one that
        # Firefox is currently showing the user, we skip it.
        #
        pursue = default.Script.pursueForFlatReview(self, obj)
        if pursue and (obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME):
            documentFrame = self.getDocumentFrame()
            pursue = obj == documentFrame

        return pursue

    def getHeadingLevel(self, obj):
        """Determines the heading level of the given object.  A value
        of 0 means there is no heading level."""

        level = 0
        
        if obj is None:
            return level

        if obj.getRole() == pyatspi.ROLE_HEADING:
            attributes = obj.getAttributes()
            if attributes is None:
                return level
            for attribute in attributes:
                if attribute.startswith("level:"):
                    level = int(attribute.split(":")[1])
                    break

        return level
            
    def getNodeLevel(self, obj):
        """ Determines the level of at which this object is at by using the
        object attribute 'level'.  To be consistent with default.getNodeLevel()
        this value is 0-based (Gecko return is 1-based) """
        
        if obj is None or obj.getRole() == pyatspi.ROLE_HEADING:
            return -1
        
        attrs = obj.getAttributes()
        if attrs is None:
            return -1
        for attr in attrs:
            if attr.startswith("level:"):
                return int(attr[6:]) - 1
        return -1

    def getTopOfFile(self):
        """Returns the object and first caret offset at the top of the
         document frame."""

        documentFrame = self.getDocumentFrame()
        [obj, offset] = self.findFirstCaretContext(documentFrame, 0)

        return [obj, offset]

    def getBottomOfFile(self):
        """Returns the object and last caret offset at the bottom of the
         document frame."""

        obj = self.getLastObject()
        offset = 0

        # obj should now be the very last item in the entire document frame
        # and not have children of its own.  Therefore, it should have text.
        # If it doesn't, we don't want to be here.
        #
        text = self.queryNonEmptyText(obj)
        if text:
            offset = text.characterCount - 1
        else:
            obj = self.findPreviousObject(obj)

        while obj:
            [lastObj, lastOffset] = self.findNextCaretInOrder(obj, offset)
            if not lastObj \
               or self.isSameObject(lastObj, obj) and (lastOffset == offset):
                break

            [obj, offset] = [lastObj, lastOffset]

        return [obj, offset]

    def getLastObject(self):
        """Returns the last object in the document frame"""

        documentFrame = self.getDocumentFrame()
        lastChild = documentFrame[documentFrame.childCount - 1]
        while lastChild:
            lastObj = self.findNextObject(lastChild)
            if lastObj:
                lastChild = lastObj
            else:
                break

        return lastChild

    def getNextCellInfo(self, cell, direction):
        """Given a cell from which to start and a direction in which to
        search locates the next cell and returns it, along with its
        text, extents (as a tuple), and whether or not the cell contents
        consist of a form field.

        Arguments
        - cell: the table cell from which to start
        - direction: a string which can be one of four options: 'left',
                     'right', 'up', 'down'

        Returns [nextCell, text, extents, isField]
        """

        newCell = None
        text = None
        extents = ()
        isField = False
        if not cell or cell.getRole() != pyatspi.ROLE_TABLE_CELL:
            return [newCell, text, extents, isField]

        [row, col] = self.getCellCoordinates(cell)
        table = cell.parent.queryTable()
        rowspan = table.getRowExtentAt(row, col)
        colspan = table.getColumnExtentAt(row, col)
        nextCell = None
        if direction == "left" and col > 0:
            nextCell = (row, col - 1)
        elif direction == "right" \
             and (col + colspan <= table.nColumns - 1):
            nextCell = (row, col + colspan)
        elif direction == "up" and row > 0:
            nextCell = (row - 1, col)
        elif direction == "down" \
             and (row + rowspan <= table.nRows - 1):
            nextCell = (row + rowspan, col)
        if nextCell:
            newCell = table.getAccessibleAt(nextCell[0], nextCell[1])
            if newCell:
                [obj, offset] = self.findFirstCaretContext(newCell, 0)
                extents = self.getExtents(obj, offset, offset + 1)
                isField = self.isFormField(obj)
                if self.queryNonEmptyText(obj) \
                   and not self.isBlankCell(newCell):
                    text = self.getDisplayedText(obj)

        return [newCell, text, extents, isField]

    def expandEOCs(self, obj, startOffset=0, endOffset= -1):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with their text.

        Arguments
        - obj: the object whose text should be expanded
        - startOffset: the offset of the first character to be included
        - endOffset: the offset of the last character to be included

        Returns the fully expanded text for the object.
        """

        if not obj:
            return None

        string = None
        text = self.queryNonEmptyText(obj)
        if text:
            string = text.getText(startOffset, endOffset)
            unicodeText = string.decode("UTF-8")
            if unicodeText \
                and self.EMBEDDED_OBJECT_CHARACTER in unicodeText:
                toBuild = list(unicodeText)
                count = toBuild.count(self.EMBEDDED_OBJECT_CHARACTER)
                for i in xrange(count):
                    index = toBuild.index(self.EMBEDDED_OBJECT_CHARACTER)
                    child = obj[i]
                    childText = self.expandEOCs(child)
                    if not childText:
                        childText = ""
                    toBuild[index] = childText.decode("UTF-8")
                string = "".join(toBuild)

        return string

    def getObjectsFromEOCs(self, obj, offset, boundary):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with [obj, startOffset, endOffset] tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - offset: the character offset after which 
        - boundary: the pyatspi text boundary type

        Returns a list of object tuples.
        """

        if not obj:
            return []

        elif obj.getRole() == pyatspi.ROLE_TABLE:
            # If this is a table, move to the first cell.
            # [[[TODOS - JD:
            #    1) It might be nice to announce the fact that we've just
            #       found a table, what its dimensions are, etc.
            #    2) It seems that down arrow moves us to the table, but up
            #       arrow moves us to the last row.  Possible side effect
            #       of our existing caret browsing implementation??]]]
            #
            obj = obj.queryTable().getAccessibleAt(0, 0)

        objects = []
        text = self.queryNonEmptyText(obj)
        if text:
            [textAtOffset, start, end] = text.getTextAtOffset(offset,
                                                              boundary)
            unicodeText = textAtOffset.decode("UTF-8")
            if unicodeText.startswith(self.EMBEDDED_OBJECT_CHARACTER):
                [textAtOffset, start, end] = text.getTextAfterOffset(offset,
                                                                     boundary)
            if textAtOffset and textAtOffset[-1] == " ":
                newEnd = len(textAtOffset) - 1
                if newEnd:
                    textAtOffset = textAtOffset[0:newEnd]
                    end -= 1
        else:
            textAtOffset = ""
            start = 0
            end = 1
        objects.append([obj, start, end])

        pattern = re.compile(self.EMBEDDED_OBJECT_CHARACTER)
        unicodeText = textAtOffset.decode("UTF-8")
        matches = re.finditer(pattern, unicodeText)
        for m in matches:
            # Adjust the last object's endOffset to the last character
            # before the EOC. Also check to see if we have a space to
            # strip out.
            #
            childOffset = m.start(0) + start
            adjustment = int(unicodeText[m.start(0) - 1] == " ")
            objects[-1][2] = childOffset - adjustment
            if objects[-1][1] == objects[-1][2]:
                # A zero-length object is an indication of something
                # whose sole contents was an EOC.  Delete it from the
                # list.
                #
                objects.pop()

            # Recursively tack on the child's objects.
            #
            childIndex = self.getChildIndex(obj, childOffset)
            child = obj[childIndex]
            objects.extend(self.getObjectsFromEOCs(child,
                                                   0,
                                                   boundary))

            # Tack on the remainder of the original object, if any.
            #
            if end > childOffset + 1:
                objects.append([obj, childOffset + 1, end])

        if obj.getRole() == pyatspi.ROLE_IMAGE and obj.childCount:
            # Imagemaps that don't have alternative text won't implement
            # the text interface, but they will have children (essentially
            # EOCs) that we need to get.
            #
            toAdd = []
            for child in obj:
                toAdd.extend(self.getObjectsFromEOCs(child, 0, boundary))
            if len(toAdd):
                if self.isSameObject(objects[-1][0], obj):
                    objects.pop()
                objects.extend(toAdd)

        return objects

    def getMeaningfulObjectsFromLine(self, line):
        """Attempts to strip a list of (obj, start, end) tuples into one
        that contains only meaningful objects."""

        if not line or not len(line):
            return []

        lineContents = []
        for item in line:
            role = item[0].getRole()

            # If it's labelling something on this line, don't move to
            # it.
            #
            if role == pyatspi.ROLE_LABEL \
               and self.isLabellingContents(item[0], line):
                continue

            # Rather than do a brute force label guess, we'll focus on
            # entries as they are the most common and their label is
            # likely on this line.  The functional label may be made up
            # of several objects, so we'll examine the strings of what
            # we've got and pop off the ones that match.
            #
            elif role == pyatspi.ROLE_ENTRY:
                labelGuess = self.guessLabelFromLine(item[0])
                index = len(lineContents) - 1
                while labelGuess and index >= 0:
                    prevItem = lineContents[index]
                    prevText = self.queryNonEmptyText(prevItem[0])
                    if prevText:
                        string = prevText.getText(prevItem[1], prevItem[2])
                        if labelGuess.endswith(string):
                            lineContents.pop()
                            length = len(labelGuess) - len(string)
                            labelGuess = labelGuess[0:length]
                        else:
                            break
                    index -= 1

            else:
                text = self.queryNonEmptyText(item[0])
                if text:
                    string = text.getText(item[1], item[2]).decode("UTF-8")
                    if not len(string.strip()):
                        continue

            lineContents.append(item)

        return lineContents

    def guessLabelFromLine(self, obj):
        """Attempts to guess what the label of an unlabeled form control
        might be by looking at surrounding contents from the same line.

        Arguments
        - obj: the form field about which to take a guess

        Returns the text which we think might be the label or None if we
        give up.
        """

        # Based on Tom Brunet's comments on how Home Page Reader
        # approached the task of guessing labels.  Please see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        #
        #  1. Text/img that precedes control in same item.
        #  2. Text/img that follows control in same item (nothing between
        #     end of text and item)
        #
        # Reverse this order for radio buttons and check boxes
        #
        guess = None
        extents = obj.queryComponent().getExtents(0)
        objExtents = [extents.x, extents.y, extents.width, extents.height]

        lineContents = self._currentLineContents
        ourIndex = self.findObjectOnLine(obj, 0, lineContents)
        if ourIndex < 0:
            lineContents = self.getLineContentsAtOffset(obj, 0)
            ourIndex = self.findObjectOnLine(obj, 0, lineContents)

        objectsOnLine = []
        for content in lineContents:
            objectsOnLine.append(content[0])

        # Now that we know where we are, let's see who are neighbors are
        # and where they are.
        #
        onLeft = None
        onRight = None
        if ourIndex > 0:
            onLeft = objectsOnLine[ourIndex - 1]
        if 0 <= ourIndex < len(objectsOnLine) - 1:
            onRight = objectsOnLine[ourIndex + 1]

        # Normally we prefer what's on the left given a choice.  Reasons
        # to prefer what's on the right include looking at a radio button
        # or a checkbox. [[[TODO - JD: Language direction should also be
        # taken into account.]]]
        #
        preferRight = obj.getRole() in [pyatspi.ROLE_CHECK_BOX,
                                        pyatspi.ROLE_RADIO_BUTTON]

        # [[[TODO: JD: Nearby text that's not actually in the form may need
        # to be ignored.  Let's try that for now and adjust based on feedback
        # and testing.]]]
        #
        leftIsInForm = self.getAncestor(onLeft,
                                        [pyatspi.ROLE_FORM],
                                        [pyatspi.ROLE_DOCUMENT_FRAME])
        rightIsInForm = self.getAncestor(onRight,
                                         [pyatspi.ROLE_FORM],
                                         [pyatspi.ROLE_DOCUMENT_FRAME])

        # If it's a radio button, we'll waive the requirement of the text
        # on the right being within the form (or rather, we'll just act as
        # if it were even if it's not).
        #
        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            rightIsInForm = True

        # [[[TODO: Grayed out buttons don't pass the isFormField() test
        # because they are neither focusable nor showing -- and thus
        # something we don't want to navigate to via structural navigation.
        # We may need to rethink our definition of isFormField().  In the
        # meantime, let's not used grayed out buttons as labels. As an
        # example, see the Search entry on live.gnome.org.]]]
        #
        if onLeft:
            leftIsFormField = self.isFormField(onLeft) \
                              or onLeft.getRole() == pyatspi.ROLE_PUSH_BUTTON
        if onRight:
            rightIsFormField = self.isFormField(onRight) \
                               or onRight.getRole() == pyatspi.ROLE_PUSH_BUTTON

        if onLeft and leftIsInForm and not leftIsFormField:
            # We want to get the text on the left including embedded objects
            # that are NOT form fields. If we find a form field on the left,
            # that will be the starting point of the text we want.
            #
            startOffset = 0
            endOffset = -1
            if self.isSameObject(obj.parent, onLeft):
                endOffset = self.getCharacterOffsetInParent(obj)
                index = obj.getIndexInParent()
                if index > 0:
                    prevSibling = onLeft[index - 1]
                    if self.isFormField(prevSibling):
                        startOffset = \
                                  self.getCharacterOffsetInParent(prevSibling)

            guess = self.expandEOCs(onLeft, startOffset, endOffset)
            if guess:
                guess = guess.decode("UTF-8").strip()
            if not guess and onLeft.getRole() == pyatspi.ROLE_IMAGE:
                guess = onLeft.name

        if (preferRight or not guess) \
           and onRight and rightIsInForm and not rightIsFormField:
            # The object's horizontal position plus its width tells us
            # where the text on the right can begin.  For now, define
            # "immediately after" as  within 50 pixels.
            #
            canStartAt = objExtents[0] + objExtents[2]
            onRightExtents = onRight.queryComponent().getExtents(0)
            onRightExtents = [onRightExtents.x, onRightExtents.y,
                              onRightExtents.width, onRightExtents.height]

            if (onRightExtents[0] - canStartAt) <= 50:
                # We want to get the text on the right including embedded
                # objects that are NOT form fields.  If we find a form field
                # on the right, that will be the ending point of the text we
                # want.  However, if we have a form field on the right and
                # do not have a reason to prefer the text on the right, our
                # label may be on the line above.  As an example, see the
                # bugzilla Advanced search... Bug Changes section.
                #
                startOffset = 0
                endOffset = -1
                if self.isSameObject(obj.parent, onRight):
                    startOffset = self.getCharacterOffsetInParent(obj)
                    index = obj.getIndexInParent()
                    if index < onRight.childCount - 1:
                        nextSibling = onRight[index + 1]
                        nextRole = nextSibling.getRole()
                        if self.isFormField(nextSibling) \
                           or nextRole == pyatspi.ROLE_RADIO_BUTTON:
                            endOffset = \
                                  self.getCharacterOffsetInParent(nextSibling)
                            if not preferRight:
                                return None

                guess = self.expandEOCs(onRight, startOffset, endOffset)
                if guess:
                    guess = guess.decode("UTF-8").strip()
                if not guess and onRight.getRole() == pyatspi.ROLE_IMAGE:
                    guess = onRight.name

        return guess

    def guessLabelFromOtherLines(self, obj):
        """Attempts to guess what the label of an unlabeled form control
        might be by looking at nearby contents from neighboring lines.

        Arguments
        - obj: the form field about which to take a guess

        Returns the text which we think might be the label or None if we
        give up.
        """

        # Based on Tom Brunet's comments on how Home Page Reader
        # approached the task of guessing labels.  Please see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        #
        guess = None
        extents = obj.queryComponent().getExtents(0)
        objExtents = \
               [extents.x, extents.y, extents.width, extents.height]

        index = self.findObjectOnLine(obj, 0, self._currentLineContents)
        if index > 0 and self._previousLineContents:
            prevLineContents = self._previousLineContents
            prevObj = prevLineContents[0][0]
            prevOffset = prevLineContents[0][1]
        else:
            [prevObj, prevOffset] = self.findPreviousLine(obj, 0)
            prevLineContents = self.getLineContentsAtOffset(prevObj,
                                                            prevOffset)
            self._previousLineContents = prevLineContents

        nextLineContents = self._nextLineContents
        if index > 0 and nextLineContents:
            nextObj = nextLineContents[0][0]
            nextOffset = nextLineContents[0][1]

        # The labels for combo boxes won't be found below the combo box
        # because expanding the combo box will cover up the label. Labels
        # for lists probably won't be below the list either.
        #
        if not nextLineContents and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                                      pyatspi.ROLE_MENU,
                                                      pyatspi.ROLE_MENU_ITEM,
                                                      pyatspi.ROLE_LIST,
                                                      pyatspi.ROLE_LIST_ITEM]:
            [nextObj, nextOffset] = self.findNextLine(obj, 0)
            nextLineContents = self.getLineContentsAtOffset(nextObj, 
                                                            nextOffset)
            self._nextLineContents = nextLineContents
        else:
            [nextObj, nextOffset] = [None, 0]
            nextLineContents = []

        above = None
        for content in prevLineContents:
            extents = content[0].queryComponent().getExtents(0)
            aboveExtents = \
                 [extents.x, extents.y, extents.width, extents.height]

            # [[[TODO: Grayed out buttons don't pass the isFormField()
            # test because they are neither focusable nor showing -- and
            # thus something we don't want to navigate to via structural
            # navigation. We may need to rethink our definition of
            # isFormField().  In the meantime, let's not used grayed out
            # buttons as labels. As an example, see the Search entry on
            # live.gnome.org. We want to ignore menu items as well.]]]
            #
            aboveIsFormField = self.isFormField(content[0]) \
                        or content[0].getRole() in [pyatspi.ROLE_PUSH_BUTTON,
                                                    pyatspi.ROLE_MENU_ITEM,
                                                    pyatspi.ROLE_LIST]

            # [[[TODO - JD: Nearby text that's not actually in the form
            # may need to be ignored.  Let's do so unless it's directly
            # above the form field or the text above is contained in the
            # form's parent and adjust based on feedback, testing.]]]
            #
            theForm = self.getAncestor(obj,
                                       [pyatspi.ROLE_FORM],
                                       [pyatspi.ROLE_DOCUMENT_FRAME])
            aboveForm = self.getAncestor(obj,
                                         [pyatspi.ROLE_FORM],
                                         [pyatspi.ROLE_DOCUMENT_FRAME])
            aboveIsInForm = self.isSameObject(theForm, aboveForm)
            formIsInAbove = theForm \
                            and self.isSameObject(theForm.parent, content[0])

            # If the horizontal starting point of the object is the
            # same as the horizontal starting point of the text
            # above it, the text above it is probably serving as the
            # label. We'll allow for a 2 pixel difference.  If that
            # fails, and the text above starts within 50 pixels to
            # the left and ends somewhere above or beyond the current
            # form field, we'll give it the benefit of the doubt.
            # For an example of the latter case, see Bugzilla's Advanced
            # search page, Bug Changes section.
            #
            if (objExtents != aboveExtents) and not aboveIsFormField:
                guessThis = (0 <= abs(objExtents[0] - aboveExtents[0]) <= 2)
                if not guessThis:
                    objEnd = objExtents[0] + objExtents[2]
                    aboveEnd = aboveExtents[0] + aboveExtents[2]
                    guessThis = (0 <= objExtents[0] - aboveExtents[0] <= 50) \
                                 and (aboveEnd > objEnd) \
                                 and (aboveIsInForm or formIsInAbove)

                if guessThis:
                    above = content[0]
                    guessAbove = self.expandEOCs(content[0],
                                                 content[1],
                                                 content[2])
                    break

        below = None
        for content in nextLineContents:
            extents = content[0].queryComponent().getExtents(0)
            belowExtents = \
                 [extents.x, extents.y, extents.width, extents.height]
            # [[[TODO: Grayed out buttons don't pass the isFormField()
            # test because they are neither focusable nor showing -- and
            # thus something we don't want to navigate to via structural
            # navigation. We may need to rethink our definition of
            # isFormField().  In the meantime, let's not used grayed out
            # buttons as labels. As an example, see the Search entry on
            # live.gnome.org. We want to ignore menu items as well.]]]
            #
            belowIsFormField = self.isFormField(content[0]) \
                        or content[0].getRole() in [pyatspi.ROLE_PUSH_BUTTON,
                                                    pyatspi.ROLE_MENU_ITEM,
                                                    pyatspi.ROLE_LIST]

            # [[[TODO - JD: Nearby text that's not actually in the form
            # may need to be ignored.  Let's try that for now and adjust
            # based on feedback and testing.]]]
            #
            belowIsInForm = self.getAncestor(content[0],
                                             [pyatspi.ROLE_FORM],
                                             [pyatspi.ROLE_DOCUMENT_FRAME])

            # If the horizontal starting point of the object is the
            # same as the horizontal starting point of the text
            # below it, the text below it is probably serving as the
            # label. We'll allow for a 2 pixel difference.
            #
            if objExtents != belowExtents \
               and not belowIsFormField \
               and belowIsInForm \
               and 0 <= abs(objExtents[0] - belowExtents[0]) <= 2:
                below = content[0]
                guessBelow = self.expandEOCs(content[0],
                                             content[1],
                                             content[2])
                break

        if above:
            if not below:
                guess = guessAbove
            else:
                # We'll guess the nearest text.
                #
                bottomOfAbove = aboveExtents[1] + aboveExtents[3]
                topOfBelow = belowExtents[1]
                bottomOfObj = objExtents[1] + objExtents[3]
                topOfObject = objExtents[1]
                aboveProximity = topOfObject - bottomOfAbove
                belowProximity = topOfBelow - bottomOfObj
                if aboveProximity <=  belowProximity \
                   or belowProximity < 0:
                    guess = guessAbove
                else:
                    guess = guessBelow
        elif below:
            guess = guessBelow

        return guess

    def guessLabelFromTable(self, obj):
        """Attempts to guess what the label of an unlabeled form control
        might be by looking at surrounding table cells.

        Arguments
        - obj: the form field about which to take a guess

        Returns the text which we think might be the label or None if we
        give up.
        """

        # Based on Tom Brunet's comments on how Home Page Reader
        # approached the task of guessing labels.  Please see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        #
        # "3. Text/img that precedes control in previous item/cell
        #     not another control in that item)..."
        #
        #  4. Text/img in cell above without other controls in this
        #     cell above."
        #
        # If that fails, we might as well look to the cell below. If the
        # text is immediately below the entry and nothing else looks like
        # a label, that text might be it. Given both text above and below
        # the control, the most likely label is probably the text that is
        # vertically nearest it. This theory will, of course, require
        # testing "in the wild."
        #
        guess = None
        extents = obj.queryComponent().getExtents(0)
        objExtents = [extents.x, extents.y, extents.width, extents.height]
        containingCell = \
                       self.getAncestor(obj,
                                        [pyatspi.ROLE_TABLE_CELL],
                                        [pyatspi.ROLE_DOCUMENT_FRAME])

        # If we're not in a table cell, pursuing this further is silly. If
        # we're in a table cell but are not the sole occupant of that cell,
        # we're likely in a more complex layout table than this approach
        # can handle.
        #
        if not containingCell \
           or (containingCell.childCount > 1):
            return guess
        elif self.getAncestor(obj,
                              [pyatspi.ROLE_PARAGRAPH],
                              [pyatspi.ROLE_TABLE,
                               pyatspi.ROLE_DOCUMENT_FRAME]):
            return guess

        [cellLeft, leftText, leftExtents, leftIsField] = \
                   self.getNextCellInfo(containingCell, "left")
        [cellRight, rightText, rightExtents, rightIsField] = \
                   self.getNextCellInfo(containingCell, "right")
        [cellAbove, aboveText, aboveExtents, aboveIsField] = \
                   self.getNextCellInfo(containingCell, "up")
        [cellBelow, belowText, belowExtents, belowIsField] = \
                   self.getNextCellInfo(containingCell, "down")

        if rightText:
            # The object's horizontal position plus its width tells us
            # where the text on the right can begin. For now, define
            # "immediately after" as  within 50 pixels.
            #
            canStartAt = objExtents[0] + objExtents[2]
            rightCloseEnough = rightExtents[0] - canStartAt <= 50

        if leftText and not leftIsField:
            guess = leftText
        elif rightText and rightCloseEnough and not rightIsField:
            guess = rightText
        elif aboveText and not aboveIsField:
            if not belowText or belowIsField:
                guess = aboveText
            else:
                # We'll guess the nearest text.
                #
                bottomOfAbove = aboveExtents[1] + aboveExtents[3]
                topOfBelow = belowExtents[1]
                bottomOfObj = objExtents[1] + objExtents[3]
                topOfObject = objExtents[1]
                aboveProximity = topOfObject - bottomOfAbove
                belowProximity = topOfBelow - bottomOfObj
                if aboveProximity <=  belowProximity:
                    guess = aboveText
                else:
                    guess = belowText
        elif belowText and not belowIsField:
            guess = belowText
        elif aboveIsField:
            # Given the lack of potential labels and the fact that
            # there's a form field immediately above us, there's
            # a reasonable chance that we're in a series of form
            # fields arranged grid-style.  It's even more likely
            # if the form fields above us are all of the same type
            # and size (say, within 1 pixel).
            #
            grid = False
            done = False
            nextCell = containingCell
            while not done:
                [nextCell, text, extents, isField] = \
                        self.getNextCellInfo(nextCell, "up")
                if nextCell:
                    dWidth = abs(objExtents[2] - extents[2])
                    dHeight = abs(objExtents[3] - extents[3])
                    if dWidth > 1 or dHeight > 1:
                        done = True
                    if not isField:
                        [row, col] = self.getCellCoordinates(nextCell)
                        if row == 0:
                            grid = True
                            done = True
                else:
                    done = True

            if grid:
                topCol = nextCell.parent.queryTable().getAccessibleAt(0, col)
                [objTop, offset] = self.findFirstCaretContext(topCol, 0)
                if self.queryNonEmptyText(topCol) \
                   and not self.isFormField(topCol):
                    guess = self.expandEOCs(topCol)

        return guess

    def guessTheLabel(self, obj):
        """Attempts to guess what the label of an unlabeled form control
        might be.

        Arguments
        - obj: the form field about which to take a guess

        Returns the text which we think might be the label or None if we
        give up.
        """

        # The initial stab at this is based on Tom Brunet's comments
        # on how Home Page Reader approached this task.  His comments
        # can be found at the RFE for Mozilla to do this work for us:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        # N.B. If you see a comment in quotes, it's taken directly from
        # Tom.
        #
        guess = None

        # If we're not in the document frame, we don't want to be guessing.
        # We also don't want to be guessing if the item doesn't have focus.
        #
        if not self.inDocumentContent() \
           or not obj.getState().contains(pyatspi.STATE_FOCUSED) \
           or self.isAriaWidget(obj):
            return guess

        # Because the guesswork is based upon spatial relations, if we're
        # in a list, look from the perspective of the first list item rather
        # than from the list as a whole.
        #
        if obj.getRole() == pyatspi.ROLE_LIST:
            obj = obj[0]

        guess = self.guessLabelFromLine(obj)
        # print "guess from line: ", guess
        if not guess:
            # Maybe it's in a table cell.
            #
            guess = self.guessLabelFromTable(obj)
            # print "guess from table: ", guess
        if not guess:
            # Maybe the text is above or below us, but not in a table
            # cell.
            #
            guess = self.guessLabelFromOtherLines(obj)
            #print "guess form other lines: ", guess
        if not guess:
            # We've pretty much run out of options.  From Tom's overview
            # of the approach for all controls:
            # "... 4. title attribute."
            # The title attribute seems to be exposed as the name.
            #
            guess = obj.name
            #print "Guessing the name: ", guess

        return guess.strip()

    ####################################################################
    #                                                                  #
    # Methods to find previous and next objects.                       #
    #                                                                  #
    ####################################################################

    def findFirstCaretContext(self, obj, characterOffset):
        """Given an object and a character offset, find the first
        [obj, characterOffset] that is actually presenting something
        on the display.  The reason we do this is that the
        [obj, characterOffset] passed in may actually be pointing
        to an embedded object character.  In those cases, we dig
        into the hierarchy to find the 'real' thing.

        Arguments:
        -obj: an accessible object
        -characterOffset: the offset of the character where to start
        looking for real rext

        Returns [obj, characterOffset] that points to real content.
        """

        text = self.queryNonEmptyText(obj)
        if text:
            unicodeText = self.getUnicodeText(obj)
            if characterOffset >= len(unicodeText):
                if obj.getRole() != pyatspi.ROLE_ENTRY:
                    return [obj, -1]
                else:
                    # We're at the end of an entry.  If we return -1,
                    # and then set the caretContext accordingly,
                    # findNextCaretInOrder() will think we're at the
                    # beginning and we'll never escape this entry.
                    #
                    return [obj, characterOffset]

            character = text.getText(characterOffset,
                                     characterOffset + 1).decode("UTF-8")
            if character == self.EMBEDDED_OBJECT_CHARACTER:
                if obj.childCount <= 0:
                    return self.findFirstCaretContext(obj, characterOffset + 1)
                try:
                    childIndex = self.getChildIndex(obj, characterOffset)
                    return self.findFirstCaretContext(obj[childIndex], 0)
                except:
                    return [obj, -1]
            else:
                # [[[TODO: WDW - HACK because Gecko currently exposes
                # whitespace from the raw HTML to us.  We can infer this
                # by seeing if the extents are nil.  If so, we skip to
                # the next character.]]]
                #
                extents = self.getExtents(obj,
                                          characterOffset,
                                          characterOffset + 1)
                if (extents == (0, 0, 0, 0)) \
                    and ((characterOffset + 1) < len(unicodeText)):
                    return self.findFirstCaretContext(obj, characterOffset + 1)
                else:
                    return [obj, characterOffset]
        else:
            return [obj, -1]

    def findNextCaretInOrder(self, obj=None,
                             startOffset=-1,
                             includeNonText=True):
        """Given an object at a character offset, return the next
        caret context following an in-order traversal rule.

        Arguments:
        - root: the Accessible to start at.  If None, starts at the
        document frame.
        - startOffset: character position in the object text field
        (if it exists) to start at.  Defaults to -1, which means
        start at the beginning - that is, the next character is the
        first character in the object.
        - includeNonText: If False, only land on objects that support the
        accessible text interface; otherwise, include logical leaf
        nodes like check boxes, combo boxes, etc.

        Returns [obj, characterOffset] or [None, -1]
        """

        if not obj:
            obj = self.getDocumentFrame()

        if not obj or not self.inDocumentContent(obj):
            return [None, -1]

        # We do not want to descend objects of certain role types.
        #
        doNotDescend = obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
                       and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                             pyatspi.ROLE_LIST]

        text = self.queryNonEmptyText(obj)
        if text and not (self.isAriaWidget(obj) \
                         and obj.getRole() == pyatspi.ROLE_LIST):
            unicodeText = self.getUnicodeText(obj)

            # Delete the final space character if we find it.  Otherwise,
            # we'll arrow to it.  (We can't just strip the string otherwise
            # we skip over blank lines that one could otherwise arrow to.)
            #
            if len(unicodeText) > 1 and unicodeText[-1] == " ":
                unicodeText = unicodeText[0:len(unicodeText) - 1]

            nextOffset = startOffset + 1
            while nextOffset < len(unicodeText):
                if unicodeText[nextOffset] != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, nextOffset]
                elif obj.childCount:
                    child = obj[self.getChildIndex(obj, nextOffset)]
                    if child:
                        return self.findNextCaretInOrder(child,
                                                         -1,
                                                       includeNonText)
                    else:
                        nextOffset += 1
                else:
                    nextOffset += 1

        # If this is a list or combo box in an HTML form, we don't want
        # to place the caret inside the list, but rather treat the list
        # as a single object.  Otherwise, if it has children, look there.
        #
        elif obj.childCount and obj[0] and not doNotDescend:
            try:
                return self.findNextCaretInOrder(obj[0],
                                                 -1,
                                                 includeNonText)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        elif includeNonText and (startOffset < 0) \
             and (not self.isLayoutOnly(obj)):
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.getDocumentFrame()
        if self.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findNextCaretInOrder(obj.parent,
                                                 characterOffsetInParent,
                                                 includeNonText)
            else:
                index = obj.getIndexInParent() + 1
                if index < obj.parent.childCount:
                    try:
                        return self.findNextCaretInOrder(
                            obj.parent[index],
                            -1,
                            includeNonText)
                    except:
                        debug.printException(debug.LEVEL_SEVERE)
            obj = obj.parent

        return [None, -1]

    def findPreviousCaretInOrder(self,
                                 obj=None,
                                 startOffset=-1,
                                 includeNonText=True):
        """Given an object an a character offset, return the previous
        caret context following an in order traversal rule.

        Arguments:
        - root: the Accessible to start at.  If None, starts at the
        document frame.
        - startOffset: character position in the object text field
        (if it exists) to start at.  Defaults to -1, which means
        start at the end - that is, the previous character is the
        last character of the object.

        Returns [obj, characterOffset] or [None, -1]
        """

        if not obj:
            obj = self.getDocumentFrame()

        if not obj or not self.inDocumentContent(obj):
            return [None, -1]

        # We do not want to descend objects of certain role types.
        #
        doNotDescend = obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
                       and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                             pyatspi.ROLE_LIST]

        text = self.queryNonEmptyText(obj)
        if text and not (self.isAriaWidget(obj) \
                         and obj.getRole() == pyatspi.ROLE_LIST):
            unicodeText = self.getUnicodeText(obj)

            # Delete the final space character if we find it.  Otherwise,
            # we'll arrow to it.  (We can't just strip the string otherwise
            # we skip over blank lines that one could otherwise arrow to.)
            #
            if len(unicodeText) > 1 and unicodeText[-1] == " ":
                unicodeText = unicodeText[0:len(unicodeText) - 1]

            if (startOffset == -1) or (startOffset > len(unicodeText)):
                startOffset = len(unicodeText)
            previousOffset = startOffset - 1
            while previousOffset >= 0:
                if unicodeText[previousOffset] \
                    != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, previousOffset]
                elif obj.childCount:
                    child = obj[self.getChildIndex(obj, previousOffset)]
                    if child:
                        return self.findPreviousCaretInOrder(child,
                                                             -1,
                                                             includeNonText)
                    else:
                        previousOffset -= 1
                else:
                    previousOffset -= 1

        # If this is a list or combo box in an HTML form, we don't want
        # to place the caret inside the list, but rather treat the list
        # as a single object.  Otherwise, if it has children, look there.
        #
        elif obj.childCount and obj[obj.childCount - 1] and not doNotDescend:
            try:
                return self.findPreviousCaretInOrder(
                    obj[obj.childCount - 1],
                    -1,
                    includeNonText)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        elif includeNonText and (startOffset < 0) \
            and (not self.isLayoutOnly(obj)):
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.getDocumentFrame()
        if self.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findPreviousCaretInOrder(obj.parent,
                                                     characterOffsetInParent,
                                                     includeNonText)
            else:
                index = obj.getIndexInParent() - 1
                if index >= 0:
                    try:
                        return self.findPreviousCaretInOrder(
                            obj.parent[index],
                            -1,
                            includeNonText)
                    except:
                        debug.printException(debug.LEVEL_SEVERE)
            obj = obj.parent

        return [None, -1]

    def findPreviousObject(self, obj):
        """Finds the object prior to this one, where the tree we're
        dealing with is a DOM and 'prior' means the previous object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        """

        previousObj = None
        characterOffset = 0
        documentFrame = self.getDocumentFrame()

        # If the object is the document frame, the previous object is
        # the one that follows us relative to our offset.
        #
        if self.isSameObject(obj, documentFrame):
            [obj, characterOffset] = self.getCaretContext()

        index = obj.getIndexInParent() - 1
        if (index < 0):
            if not self.isSameObject(obj, documentFrame):
                previousObj = obj.parent
            else:
                # We're likely at the very end of the document
                # frame.
                previousObj = self.getLastObject()
        else:
            # [[[TODO: HACK - WDW defensive programming because Gecko
            # ally hierarchies are not always working.  Objects say
            # they have children, but these children don't exist when
            # we go to get them.  So...we'll just keep going backwards
            # until we find a real child that we can work with.]]]
            #
            while not isinstance(previousObj, 
                                 pyatspi.Accessibility.Accessible) \
                and index >= 0:
                previousObj = obj.parent[index]
                index -= 1

            # Now that we're at a child we can work with, we need to
            # look at it further.  It could be the root of a hierarchy.
            # In that case, the last child in this hierarchy is what
            # we want.  So, we dive down the 'right hand side' of the
            # tree to get there.
            #
            # [[[TODO: HACK - WDW we need to be defensive because of
            # Gecko's broken a11y hierarchies, so we make this much
            # more complex than it really has to be.]]]
            #
            if not previousObj:
                if not self.isSameObject(obj, documentFrame):
                    previousObj = obj.parent
                else:
                    previousObj = obj

            role = previousObj.getRole()
            if role == pyatspi.ROLE_MENU_ITEM:
                return previousObj.parent.parent
            elif role == pyatspi.ROLE_LIST_ITEM:
                parent = previousObj.parent
                if parent.getState().contains(pyatspi.STATE_FOCUSABLE) \
                   and not self.isAriaWidget(parent):
                    return parent

            while previousObj.childCount:
                role = previousObj.getRole()
                state = previousObj.getState()
                if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_MENU]:
                    break
                elif role == pyatspi.ROLE_LIST \
                     and state.contains(pyatspi.STATE_FOCUSABLE) \
                     and not self.isAriaWidget(previousObj):
                    break

                index = previousObj.childCount - 1
                while index >= 0:
                    child = previousObj[index]
                    childOffset = self.getCharacterOffsetInParent(child)
                    if isinstance(child, pyatspi.Accessibility.Accessible) \
                       and not (self.isSameObject(previousObj, documentFrame) \
                        and childOffset > characterOffset):
                        previousObj = child
                        break
                    else:
                        index -= 1
                if index < 0:
                    break

        if self.isSameObject(previousObj, documentFrame):
            previousObj = None

        return previousObj

    def findNextObject(self, obj):
        """Finds the object after to this one, where the tree we're
        dealing with is a DOM and 'next' means the next object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        """

        nextObj = None
        characterOffset = 0
        documentFrame = self.getDocumentFrame()

        # If the object is the document frame, the next object is
        # the one that follows us relative to our offset.
        #
        if self.isSameObject(obj, documentFrame):
            [obj, characterOffset] = self.getCaretContext()

        # If the object has children, we'll choose the first one,
        # unless it's a combo box or a focusable HTML list.
        #
        # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
        # a bit of a challenge.]]]
        #
        role = obj.getRole()
        if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_MENU]:
            descend = False
        elif role == pyatspi.ROLE_LIST \
            and obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
            and not self.isAriaWidget(obj):
            descend = False
        else:
            descend = True

        index = 0
        while descend and index < obj.childCount:
            child = obj[index]
            # bandaid for Gecko broken hierarchy
            if child is None:
                index += 1
                continue
            childOffset = self.getCharacterOffsetInParent(child)
            if isinstance(child, pyatspi.Accessibility.Accessible) \
               and not (self.isSameObject(obj, documentFrame) \
                        and childOffset < characterOffset):
                nextObj = child
                break
            else:
                index += 1

        # Otherwise, we'll look to the next sibling.
        #
        # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
        # a bit of a challenge.]]]
        #
        if not nextObj:
            index = obj.getIndexInParent() + 1
            while index < obj.parent.childCount:
                child = obj.parent[index]
                if isinstance(child, pyatspi.Accessibility.Accessible):
                    nextObj = child
                    break
                else:
                    index += 1

        # If there is no next sibling, we'll move upwards.
        #
        candidate = obj
        while not nextObj:
            # Go up until we find a parent that might have a sibling to
            # the right for us.
            #
            while (candidate.getIndexInParent() >= \
                  (candidate.parent.childCount - 1)) \
                and not self.isSameObject(candidate, documentFrame):
                candidate = candidate.parent

            # Now...let's get the sibling.
            #
            # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
            # a bit of a challenge.]]]
            #
            if not self.isSameObject(candidate, documentFrame):
                index = candidate.getIndexInParent() + 1
                while index < candidate.parent.childCount:
                    child = candidate.parent[index]
                    if isinstance(child, pyatspi.Accessibility.Accessible):
                        nextObj = child
                        break
                    else:
                        index += 1

                # We've exhausted trying to get all the children, but
                # Gecko's broken hierarchy has failed us for all of
                # them.  So, we need to go higher.
                #
                candidate = candidate.parent
            else:
                break

        return nextObj

    def findPreviousRole(self, roles, wrap, currentObj=None):
        """Finds the caret offset at the beginning of the next object
        using the given roles list as a pattern to match.

        Arguments:
        -roles: a list of roles from rolenames.py
        -wrap: if True and the top of the document is reached, move
               to the bottom and keep looking.
        -currentObj: the object from which the search should begin

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """

        if not currentObj:
            [currentObj, characterOffset] = self.getCaretContext()

        ancestors = []
        nestableRoles = [pyatspi.ROLE_LIST, pyatspi.ROLE_TABLE]
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        wrapped = False
        obj = self.findPreviousObject(currentObj)
        while obj:
            isNestedItem = ((obj != currentObj.parent) \
                            and (currentObj.parent.getRole() == obj.getRole()) \
                            and (obj.getRole() in nestableRoles))
            if ((not obj in ancestors) or isNestedItem) \
               and (obj.getRole() in roles) \
               and (not self.isLayoutOnly(obj)):
                if wrapped and self.isSameObject(currentObj, obj):
                    obj = None
                return [obj, wrapped]
            else:
                obj = self.findPreviousObject(obj)
                if not obj and wrap and not wrapped:
                    obj = self.getLastObject()
                    wrapped = True

        return [None, wrapped]

    def findNextRole(self, roles, wrap, currentObj=None):
        """Finds the caret offset at the beginning of the next object
        using the given roles list as a pattern to match or not match.

        Arguments:
        -roles: a list of roles from rolenames.py
        -wrap: if True and the bottom of the document is reached, move
               to the top and keep looking.
        -currentObj: the object from which the search should begin

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """

        if not currentObj:
            [currentObj, characterOffset] = self.getCaretContext()

        ancestors = []
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        wrapped = False
        obj = self.findNextObject(currentObj)
        if not obj and wrap:
            documentFrame = self.getDocumentFrame()
            obj = documentFrame[0]
            wrapped = True
        while obj:
            if (not obj in ancestors) and (obj.getRole() in roles) \
                and (not self.isLayoutOnly(obj)):
                if wrapped and self.isSameObject(currentObj, obj):
                    obj = None
                return [obj, wrapped]
            else:
                obj = self.findNextObject(obj)
                if not obj and wrap and not wrapped:
                    documentFrame = self.getDocumentFrame()
                    obj = documentFrame[0]
                    wrapped = True

        return [None, wrapped]
                
    def findPrevByPredicate(self, pred, wrap, currentObj=None):
        """Finds the caret offset at the beginning of the previous object
        using the given predicate as a pattern to match.

        Arguments:
        -pred: a python callable that takes an accessible argument and
               returns true/false based on some match criteria
        -wrap: if True and the top of the document is reached, move
               to the bottom and keep looking.
        -currentObj: the object from which the search should begin

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """

        if not currentObj:
            [currentObj, characterOffset] = self.getCaretContext()

        ancestors = []
        nestableRoles = [pyatspi.ROLE_LIST, pyatspi.ROLE_TABLE]
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        wrapped = False
        obj = self.findPreviousObject(currentObj)
        while obj:
            isNestedItem = ((obj != currentObj.parent) \
                            and (currentObj.parent.getRole() == obj.getRole()) \
                            and (obj.getRole() in nestableRoles))
            if ((not obj in ancestors) or isNestedItem) and pred(obj):
                if wrapped and self.isSameObject(currentObj, obj):
                    obj = None
                return [obj, wrapped]
            else:
                obj = self.findPreviousObject(obj)
                if not obj and wrap and not wrapped:
                    obj = self.getLastObject()
                    wrapped = True

        return [None, wrapped]
                
    def findNextByPredicate(self, pred, wrap, currentObj=None):
        """Finds the caret offset at the beginning of the next object
        using the given predicate as a pattern to match or not match.

        Arguments:
        -pred: a python callable that takes an accessible argument and
               returns true/false based on some match criteria
        -wrap: if True and the bottom of the document is reached, move
               to the top and keep looking.
        -currentObj: the object from which the search should begin

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """

        if not currentObj:
            [currentObj, characterOffset] = self.getCaretContext()
        ancestors = []
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        wrapped = False
        obj = self.findNextObject(currentObj)
        if not obj and wrap:
            documentFrame = self.getDocumentFrame()
            obj = documentFrame[0]
            wrapped = True

        while obj:
            if (not obj in ancestors) and pred(obj):
                if wrapped and self.isSameObject(currentObj, obj):
                    obj = None
                return [obj, wrapped]
            else:
                obj = self.findNextObject(obj)
                if not obj and wrap and not wrapped:
                    documentFrame = self.getDocumentFrame()
                    obj = documentFrame[0]
                    wrapped = True

        return [None, wrapped]

    ####################################################################
    #                                                                  #
    # Methods to get information about current object.                 #
    #                                                                  #
    ####################################################################

    def clearCaretContext(self):
        """Deletes all knowledge of a character context for the current
        document frame."""

        documentFrame = self.getDocumentFrame()
        self._destroyLineCache()
        try:
            del self._documentFrameCaretContext[hash(documentFrame)]
        except:
            pass

    def setCaretContext(self, obj=None, characterOffset=-1):
        """Sets the caret context for the current document frame."""

        # We keep a context for each page tab shown.
        # [[[TODO: WDW - probably should figure out how to destroy
        # these contexts when a tab is killed.]]]
        #
        documentFrame = self.getDocumentFrame()

        if not documentFrame:
            return

        self._documentFrameCaretContext[hash(documentFrame)] = \
            [obj, characterOffset]

        self._updateLineCache(obj, characterOffset)

    def getCaretContext(self, includeNonText=True):
        """Returns the current [obj, caretOffset] if defined.  If not,
        it returns the first [obj, caretOffset] found by an in order
        traversal from the beginning of the document."""

        # We keep a context for each page tab shown.
        # [[[TODO: WDW - probably should figure out how to destroy
        # these contexts when a tab is killed.]]]
        #
        documentFrame = self.getDocumentFrame()

        if not documentFrame:
            return [None, -1]

        try:
            return self._documentFrameCaretContext[hash(documentFrame)]
        except:
            self._documentFrameCaretContext[hash(documentFrame)] = \
                self.findNextCaretInOrder(None,
                                          -1,
                                          includeNonText)

        return self._documentFrameCaretContext[hash(documentFrame)]

    def getCharacterAtOffset(self, obj, characterOffset):
        """Returns the character at the given characterOffset in the
        given object or None if the object does not implement the
        accessible text specialization.
        """

        try:
            unicodeText = self.getUnicodeText(obj)
            return unicodeText[characterOffset].encode("UTF-8")
        except:
            return None

    def getWordContentsAtOffset(self, obj, characterOffset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the given object and characterOffset.  The first element in
        the list represents the beginning of the word.  The last
        element in the list represents the character just before the
        beginning of the next word.

        Arguments:
        -obj: the object to start at
        -characterOffset: the characterOffset in the object
        """

        if not obj:
            return []

        # If we're looking for the current word, we'll search
        # backwards to the beginning the current word and then
        # forwards to the beginning of the next word.  Objects that do
        # not implement text are treated as a word.
        #
        contents = []

        encounteredText = False
        [lastObj, lastCharacterOffset] = [obj, characterOffset]
        while obj == lastObj:
            if not self.queryNonEmptyText(obj):
                break
            else:
                character = self.getCharacterAtOffset(obj, characterOffset)
                if self.isWordDelimiter(character):
                    if encounteredText:
                        break
                else:
                    encounteredText = True

            [lastObj, lastCharacterOffset] = [obj, characterOffset]
            [obj, characterOffset] = \
                  self.findPreviousCaretInOrder(obj, characterOffset)

        contents.append([lastObj,
                         lastCharacterOffset,
                         lastCharacterOffset + 1])

        encounteredText = False
        encounteredDelimiter = False
        [obj, characterOffset] = [lastObj, lastCharacterOffset]
        while obj and (obj == lastObj):
            if not self.queryNonEmptyText(obj):
                break
            else:
                character = self.getCharacterAtOffset(obj, characterOffset)
                if not self.isWordDelimiter(character):
                    if encounteredText and encounteredDelimiter:
                        break
                    encounteredText = True
                else:
                    encounteredDelimiter = True

            [lastObj, lastCharacterOffset] = [obj, characterOffset]
            [obj, characterOffset] = \
                  self.findNextCaretInOrder(obj, characterOffset)
            contents[-1][2] = lastCharacterOffset + 1

        return contents

    def altGetLineContents(self, obj, offset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the given object and characterOffset.  The first element in
        the list represents the beginning of the line.  The last
        element in the list represents the character just before the
        beginning of the next line.

        Arguments:
        -obj: the object to start at
        -offset: the character offset in the object
        """

        if not obj:
            return []

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START

        # Work up the hierarchy to locate the ancestor that begins on
        # this line.
        #
        extents = self.getExtents(obj, offset, offset + 1)
        while not obj.getRole() in [pyatspi.ROLE_DOCUMENT_FRAME,
                                    pyatspi.ROLE_TABLE_CELL,
                                    pyatspi.ROLE_SECTION,
                                    pyatspi.ROLE_PANEL,
                                    pyatspi.ROLE_TEXT]:
            offsetInParent = self.getCharacterOffsetInParent(obj)
            parentExtents = self.getExtents(obj.parent,
                                            offsetInParent,
                                            offsetInParent + 1)
            if not self.onSameLine(extents, parentExtents):
                break
            offset = offsetInParent
            obj = obj.parent

        # Find the beginning of the line.
        #
        text = self.queryNonEmptyText(obj)
        singleLine = False
        if text:
            line = text.getTextAtOffset(offset, boundary)
            singleLine = (line[1] == 0) and (line[2] == text.characterCount)
            if line[2] < offset:
                index = self.getChildIndex(obj, line[1])
                if index >= 0:
                    # The start of the line is a link that started on the
                    # previous line.  We'll set obj to it and get the
                    # rest of the line later.
                    #
                    child = obj[index]
                    text = self.queryNonEmptyText(child)
                    if text:
                        line = text.getTextAtOffset(text.characterCount, 
                                                    boundary)
                        obj = child
                        offset = line[1]
            else:
                offset = line[1]

        # Move to the left to see if there's a sibling on this line which
        # we should include.
        #
        index = obj.getIndexInParent()
        sibling = obj
        role = obj.getRole()
        while sibling and index > 0:
            sibling = obj.parent[index - 1]
            siblingExtents = self.getExtents(sibling, 0, 1)

            if not self.onSameLine(extents, siblingExtents) or not singleLine:
                break
            else:
                text = self.queryNonEmptyText(sibling)
                if text:
                    line = text.getTextAtOffset(offset, boundary)
                    singleLine = (line[1] == 0) \
                             and (line[2] == text.characterCount)
                    if not singleLine \
                       or role == pyatspi.ROLE_SECTION == sibling.getRole():
                        break

            obj = sibling
            offset = 0
            index -= 1

        # Get the objects on this line.
        #
        objects = self.getObjectsFromEOCs(obj, offset, boundary)

        # Get rid of any that are zero-sized as for all intents and
        # purposes, they're not on the line.  We see this with empty
        # links: <a href="someurl"></a>
        #
        for o in objects:
            if o[2] - o[1] <= 1:
                objExtents = self.getExtents(o[0], o[1], o[2])
                if (objExtents[0] and objExtents[1]) \
                    and not (objExtents[2] and objExtents[3]) \
                    and len(objects) > 1:
                    objects.pop(objects.index(o))

        # If we're in a table cell, get the remainder of the cells
        # in the row.  But first we'll check to be sure that the
        # column doesn't span the entire row.  We also need to be
        # sure it's a cell inside a table.  (See Mozilla bug #409009).
        #
        cell = None
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            cell = obj
        elif len(objects) \
             and objects[-1][0].getRole() == pyatspi.ROLE_TABLE_CELL:
            cell = objects[-1][0]
        containingTable = self.getAncestor(cell,
                                           [pyatspi.ROLE_TABLE],
                                           [pyatspi.ROLE_DOCUMENT_FRAME])
        if containingTable:
            table = containingTable.queryTable()
            if table.nColumns <= 0:
                cell = None
            elif cell.parent == containingTable:
                index = cell.getIndexInParent()
            else:
                index = cell.parent.getIndexInParent()
            row = table.getRowAtIndex(index)
            col = table.getColumnAtIndex(index)
            col += table.getColumnExtentAt(row, col)

            if cell:
                cellContents = []
                while singleLine and col < table.nColumns:
                    cell = table.getAccessibleAt(row, col)
                    if not cell:
                        break

                    text = self.queryNonEmptyText(cell)
                    if text:
                        line = text.getTextAtOffset(offset, boundary)
                        singleLine = line[1] == 0 \
                                     and line[2] == text.characterCount

                    colspan = table.getColumnExtentAt(row, col)
                    col += colspan
                    cellContents.extend(self.getObjectsFromEOCs(cell,
                                                                0,
                                                                boundary))
                if singleLine:
                    objects.extend(cellContents)

        # We need to find out if we've started from an embedded object.
        # If we have, we'll want to include whatever follows this object
        # on the same line.
        #
        if not obj.getRole() in [pyatspi.ROLE_DOCUMENT_FRAME,
                                 pyatspi.ROLE_SECTION]:
            text = self.queryNonEmptyText(obj.parent)
            if text:
                offset = self.getCharacterOffsetInParent(obj) + 1
                atOffset = text.getTextAtOffset(offset, boundary)
                afterOffset = text.getTextAfterOffset(offset, boundary)
                if atOffset[1] < afterOffset[1] < afterOffset[2]:
                    # We're on an EOC with more text on this line.
                    #
                    objects.extend(self.getObjectsFromEOCs(obj.parent,
                                                           offset,
                                                           boundary))

        # There may be objects that are not *quite* on this line, but are
        # more or less on this line.  This can be seen with the search form
        # currently at live.gnome.org.
        #
        if objects and singleLine:
            nextObject = self.findNextObject(objects[-1][0])
            if nextObject \
              and not nextObject.parent in [obj, objects[-1][0]]:
                toAdd = self.getObjectsFromEOCs(nextObject, 0, boundary)
                if toAdd:
                    objExtents = self.getExtents(toAdd[0][0],
                                                 toAdd[0][1],
                                                 toAdd[0][2])
                    if self.onSameLine(extents, objExtents) \
                       and extents != objExtents:
                        objects.extend(toAdd)

        # Check to see that the objects that claimed to be on this line
        # really are on the same line as what we started with.
        #
        while len(objects) > 1:
            last = objects[-1]
            lastExtents = self.getExtents(last[0], last[1], last[2])
            if not self.onSameLine(extents, lastExtents) \
               and obj.getRole() != pyatspi.ROLE_TABLE_CELL:
                objects.pop()
            else:
                break

        # [[[TODO - JD: We're getting the newline character at the end
        # of links and other objects.  Ultimately, we might want to keep
        # it  around for the purpose of placing the caret on the next
        # line. Or we might not. :-) For now the goal is to make this
        # alternative method return the very same contents as our current
        # getLineContentsAtOffset(), which does not include these newline
        # chars.]]]
        #
        [obj, start, end] = objects[-1]
        text = self.queryNonEmptyText(obj)
        if text and (end - start > 1) and \
           text.getText(end - 1, end) == "\n":
            objects[-1][2] -= 1

        return objects

    def getLineContentsAtOffset(self, obj, characterOffset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the given object and characterOffset.  The first element in
        the list represents the beginning of the line.  The last
        element in the list represents the character just before the
        beginning of the next line.

        Arguments:
        -obj: the object to start at
        -characterOffset: the characterOffset in the object
        """

        if not obj:
            return []

        if performanceEnhancements:
            myContents = self.altGetLineContents(obj,
                                                 characterOffset)
            return myContents
        
        # If we're looking for the current word, we'll search
        # backwards to the beginning the current line and then
        # forwards to the beginning of the next line.
        #
        contents = []

        lineExtents = self.getExtents(
            obj, characterOffset, characterOffset + 1)

        [lastObj, lastCharacterOffset] = [obj, characterOffset]

        # If we're in a focused HTML list, treat this object as if
        # it's the only thing on this line.
        #
        limitToThis = obj.getState().contains(pyatspi.STATE_FOCUSED) \
                      and obj.getRole() in [pyatspi.ROLE_LIST_ITEM,
                                            pyatspi.ROLE_LIST]

        while obj and not limitToThis:
            [obj, characterOffset] = \
                  self.findPreviousCaretInOrder(obj, characterOffset)

            extents = self.getExtents(
                obj, characterOffset, characterOffset + 1)

            # [[[TODO: WDW - HACK.  I think we end up with a zero
            # sized character when the accessible text implementation
            # of Gecko gives us whitespace that is not visible, but
            # is in the raw HTML source.  This should hopefully be
            # fixed at some point, but we just ignore it for now.
            #
            if extents != (0, 0, 0, 0):
                if lineExtents == (0, 0, 0, 0):
                    lineExtents = extents
                elif not self.onSameLine(extents, lineExtents):
                    break
                else:
                    lineExtents = self.getBoundary(lineExtents, extents)
                    [lastObj, lastCharacterOffset] = [obj, characterOffset]

            # [[[TODO: JD - HACK. The numbers/bullets of a list item will
            # have extents of (0, 0, 0, 0).  We need to work around this
            # for now.  See bug #416971.]]]
            #
            elif obj.getRole() == pyatspi.ROLE_LIST_ITEM:
                [lastObj, lastCharacterOffset] = [obj, characterOffset]

        # [[[TODO: WDW - efficiency alert - we could always start from
        # what was passed in rather than starting at the beginning of
        # the line.  I just want to make this work for now, though.]]]
        #
        [obj, characterOffset] = [lastObj, lastCharacterOffset]
        while obj:
            extents = self.getExtents(
                obj, characterOffset, characterOffset + 1)

            # [[[TODO: WDW - HACK.  I think we end up with a zero
            # sized character when the accessible text implementation
            # of Gecko gives us whitespace that is not visible, but
            # is in the raw HTML source.  This should hopefully be
            # fixed at some point, but we just ignore it for now.
            #
            if extents != (0, 0, 0, 0):
                if obj.getRole() == pyatspi.ROLE_MENU_ITEM \
                   and not obj.getState().contains(pyatspi.STATE_SHOWING):
                    # If a combo box is on the current line, only append the
                    # menu item which is showing.
                    #
                    pass
                elif not self.onSameLine(extents, lineExtents) \
                     or (limitToThis and (lastObj != obj)):
                    break
                elif (lastObj == obj) and len(contents):
                    contents[-1][2] = characterOffset + 1
                else:
                    contents.append([obj,
                                     characterOffset,
                                     characterOffset + 1])
                lineExtents = self.getBoundary(lineExtents, extents)
                [lastObj, lastCharacterOffset] = [obj, characterOffset]

            # [[[TODO: JD - HACK. The numbers/bullets of a list item will
            # have extents of (0, 0, 0, 0).  We need to work around this
            # for now.  See bug #416971.]]]
            #
            elif (obj.getRole() == pyatspi.ROLE_LIST_ITEM) and (lastObj == obj):
                if len(contents):
                    contents[-1][2] = characterOffset + 1
                else:
                    contents.append([obj,
                                     characterOffset,
                                     characterOffset + 1])
                [lastObj, lastCharacterOffset] = [obj, characterOffset]

            [obj, characterOffset] = \
                  self.findNextCaretInOrder(obj, characterOffset)

        return contents

    def getObjectContentsAtOffset(self, obj, characterOffset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
        via an in-order traversal of the document contents starting and
        stopping at the given object.
        """

        #if not obj.getState().contains(pyatspi.STATE_SHOWING):
        #    return [[None, -1, -1]]

        if not self.queryNonEmptyText(obj):
            return [[obj, -1, -1]]

        contents = []
        text = self.getUnicodeText(obj)
        for offset in range(characterOffset, len(text)):
            if text[offset] == self.EMBEDDED_OBJECT_CHARACTER:
                child = obj[self.getChildIndex(obj, offset)]
                if child:
                    contents.extend(self.getObjectContentsAtOffset(child, 0))
            elif len(contents):
                [currentObj, startOffset, endOffset] = contents[-1]
                if obj == currentObj:
                    contents[-1] = [obj, startOffset, offset + 1]
                else:
                    contents.append([obj, offset, offset + 1])
            else:
                contents.append([obj, offset, offset + 1])

        return contents

    ####################################################################
    #                                                                  #
    # Methods to speak current objects.                                #
    #                                                                  #
    ####################################################################

    def getACSS(self, obj, string):
        """Returns the ACSS to speak anything for the given obj."""
        if obj.getRole() == pyatspi.ROLE_LINK:
            acss = self.voices[settings.HYPERLINK_VOICE]
        elif string and string.isupper() and string.strip().isalpha():
            acss = self.voices[settings.UPPERCASE_VOICE]
        else:
            acss = self.voices[settings.DEFAULT_VOICE]

        return acss

    def getUtterancesFromContents(self, contents, speakRole=True):
        """Returns a list of [text, acss] tuples based upon the
        list of [obj, startOffset, endOffset] tuples passed in.

        Arguments:
        -contents: a list of [obj, startOffset, endOffset] tuples
        -speakRole: if True, speak the roles of objects
        """

        if not len(contents):
            return []

        utterances = []
        for content in contents:
            [obj, startOffset, endOffset] = content
            if not obj:
                continue

            # If this is a label that's labelling something else, we'll
            # get the label via a speech generator -- unless it's a
            # focusable list that doesn't have focus.
            #
            labelledContent = self.isLabellingContents(obj, contents)
            if labelledContent \
               and labelledContent.getRole() != pyatspi.ROLE_LIST:
                continue

            # The radio button's label gets added to the context in
            # default.locusOfFocusChanged() and not through the speech
            # generator -- unless we wind up having to guess the label.
            # Therefore, if we have a valid label for a radio button,
            # we need to add it here.
            #
            if (obj.getRole() == pyatspi.ROLE_RADIO_BUTTON) \
                and not self.isAriaWidget(obj):
                label = self.getDisplayedLabel(obj)
                if label:
                    utterances.append([label, self.getACSS(obj, label)])

            # We only want to announce the heading role and level if we
            # have found the final item in that heading, or if that
            # heading contains no children.
            #
            containingHeading = \
                self.getAncestor(obj,
                                 [pyatspi.ROLE_HEADING],
                                 [pyatspi.ROLE_DOCUMENT_FRAME])
            isLastObject = contents.index(content) == (len(contents) - 1)
            if obj.getRole() == pyatspi.ROLE_HEADING:
                speakThisRole = isLastObject or not obj.childCount
            else:
                # We also don't want to speak the role if it's a documement
                # frame or a table cell.  In addition, if the object is an
                # entry or password_text, _getSpeechForText() will add the
                # role after the label and before any text that is present
                # in that field.  We don't want to repeat the role.
                #
                speakThisRole = \
                    not obj.getRole() in [pyatspi.ROLE_DOCUMENT_FRAME,
                                          pyatspi.ROLE_TABLE_CELL,
                                          pyatspi.ROLE_ENTRY,
                                          pyatspi.ROLE_PASSWORD_TEXT]
            text = self.queryNonEmptyText(obj)
            if self.isAriaWidget(obj):
                # Treat ARIA widgets like normal default.py widgets
                #
                speakThisRole = False
                strings = self.speechGenerator.getSpeech(obj, False)
            elif text \
               and not obj.getRole() in [pyatspi.ROLE_ENTRY,
                                         pyatspi.ROLE_PASSWORD_TEXT,
                                         pyatspi.ROLE_RADIO_BUTTON,
                                         pyatspi.ROLE_MENU_ITEM]:
                strings = [text.getText(startOffset, endOffset)]
                if strings == [' '] and len(contents) > 1:
                    strings = []
            elif self.isLayoutOnly(obj):
                continue
            else:
                strings = self.speechGenerator.getSpeech(obj, False)


        # Pylint is confused and flags these errors:
        #
        # E1101:6957:Script.getUtterancesFromContents: Instance of 
        # 'SpeechGenerator' has no 'getSpeechForObjectRole' member
        # E1101:6962:Script.getUtterancesFromContents: Instance of 
        # 'SpeechGenerator' has no 'getSpeechForObjectRole' member
        #
        # So for now, we just disable these errors in this method.
        #
        # pylint: disable-msg=E1101

            if speakRole and speakThisRole:
                if text:
                    strings.extend(\
                       self.speechGenerator.getSpeechForObjectRole(obj))

                if containingHeading and isLastObject:
                    obj = containingHeading
                    strings.extend(\
                        self.speechGenerator.getSpeechForObjectRole(obj))

            for string in strings:
                utterances.append([string, self.getACSS(obj, string)])

            if speakRole and \
               speakThisRole and \
               obj.getRole() == pyatspi.ROLE_HEADING:
                level = self.getHeadingLevel(obj)
                if level:
                    utterances.append([" ", self.getACSS(obj, " ")])
                    # Translators: this is in reference to a heading level
                    # in HTML (e.g., For <h3>, the level is 3).
                    #
                    utterances.append([_("level %d") % level, None])

        return utterances

    def clumpUtterances(self, utterances):
        """Returns a list of utterances clumped together by acss.

        Arguments:
        -utterances: unclumped utterances
        -speakRole: if True, speak the roles of objects
        """

        clumped = []

        for [string, acss] in utterances:
            if len(clumped) == 0:
                clumped = [[string, acss]]
            elif acss == clumped[-1][1]:
                clumped[-1][0] += " " + string
            else:
                clumped.append([string, acss])

        if (len(clumped) == 1) and (clumped[0][0] == "\n"):
            if settings.speakBlankLines:
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                return [[_("blank"), clumped[0][1]]]

        return clumped

    def speakContents(self, contents, speakRole=True):
        """Speaks each string in contents using the associated voice/acss"""
        utterances = self.getUtterancesFromContents(contents, speakRole)
        clumped = self.clumpUtterances(utterances)
        for [string, acss] in clumped:
            string = self.adjustForRepeats(string)
            speech.speak(string, acss, False)

    def speakCharacterAtOffset(self, obj, characterOffset):
        """Speaks the character at the given characterOffset in the
        given object."""
        character = self.getCharacterAtOffset(obj, characterOffset)
        if obj:
            if character and character != self.EMBEDDED_OBJECT_CHARACTER:
                speech.speak(character, self.getACSS(obj, character), False)
            elif obj.getRole() != pyatspi.ROLE_ENTRY:
                # We won't have a character if we move to the end of an
                # entry (in which case we're not on a character and therefore
                # have nothing to say), or when we hit a component with no
                # text (e.g. checkboxes) or reset the caret to the parent's
                # characterOffset (lists).  In these latter cases, we'll just
                # speak the entire component.
                #
                utterances = self.speechGenerator.getSpeech(obj, False)
                speech.speakUtterances(utterances)

    ####################################################################
    #                                                                  #
    # Methods to navigate to previous and next objects.                #
    #                                                                  #
    ####################################################################

    def setCaretPosition(self, obj, characterOffset):
        """Sets the caret position to the given character offset in the
        given object.
        """

        caretContext = self.getCaretContext()

        # Save where we are in this particular document frame.
        # We do this because the user might have several URLs
        # open in several different tabs, and we keep track of
        # where the caret is for each documentFrame.
        #
        documentFrame = self.getDocumentFrame()
        if documentFrame:
            self._documentFrameCaretContext[documentFrame] = caretContext

        if caretContext == [obj, characterOffset]:
            return

        self.setCaretContext(obj, characterOffset)

        # If we're not in a table cell, reset self.lastTableCell.
        #
        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            cell = self.getAncestor(obj,
                                    [pyatspi.ROLE_TABLE_CELL],
                                    [pyatspi.ROLE_DOCUMENT_FRAME])
            if not cell:
                self.lastTableCell = [-1, -1]

        # If the item is a focusable list in an HTML form, we're here
        # because we've arrowed to it.  We don't want to grab focus on
        # it and trap the user in the list. The same is true for combo
        # boxes.
        #
        if obj.getRole() in [pyatspi.ROLE_LIST, pyatspi.ROLE_COMBO_BOX] \
           and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            characterOffset = self.getCharacterOffsetInParent(obj)
            obj = obj.parent
            self.setCaretContext(obj, characterOffset)

        # Reset focus if need be.
        #
        if obj != orca_state.locusOfFocus:
            orca.setLocusOfFocus(None, obj, False)

            # We'd like the object to have focus if it can take focus.
            # Otherwise, we bubble up until we find a parent that can
            # take focus.  This is to allow us to help force focus out
            # of something such as a text area and back into the
            # document content.
            #
            self._objectForFocusGrab = obj
            while self._objectForFocusGrab and obj:
                if self._objectForFocusGrab.getState().contains(\
                    pyatspi.STATE_FOCUSABLE):
                    # If we're on an image that's in a link and the link
                    # contains more text than the EOC that represents the
                    # image, we are in danger of getting stuck on the link
                    # should we grab focus on it.
                    #
                    role = self._objectForFocusGrab.getRole()
                    if role == pyatspi.ROLE_LINK \
                       and obj.getRole() == pyatspi.ROLE_IMAGE:
                        text = self.queryNonEmptyText(self._objectForFocusGrab)
                        if text and text.characterCount > 1:
                            self._objectForFocusGrab = None
                    break
                else:
                    self._objectForFocusGrab = self._objectForFocusGrab.parent

            if self._objectForFocusGrab:
                # [[[See https://bugzilla.mozilla.org/show_bug.cgi?id=363214.
                # We need to set focus on the parent of the document frame.]]]
                #
                # [[[WDW - additional note - just setting focus on the
                # first focusable object seems to do the trick, so we
                # won't follow the advice from 363214.  Besides, if we
                # follow that advice, it doesn't work.]]]
                #
                #if objectForFocus.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
                #    objectForFocus = objectForFocus.parent
                self._objectForFocusGrab.queryComponent().grabFocus()

        # If there is a character there, we'd like to position the
        # caret the right spot.  [[[TODO: WDW - numbered lists are
        # whacked in that setting the caret offset somewhere in
        # the number will end up positioning the caret at the end
        # of the list.]]]
        #
        character = self.getCharacterAtOffset(obj, characterOffset)
        if character:
            if self.isAriaWidget() \
               or useNewLineNav \
               or not (obj.getRole() == pyatspi.ROLE_LIST_ITEM \
                     and not obj.getState().contains(pyatspi.STATE_FOCUSABLE)):
                obj.queryText().setCaretOffset(characterOffset)
                mag.magnifyAccessible(None,
                                      obj,
                                      self.getExtents(obj,
                                                      characterOffset,
                                                      characterOffset + 1))

    def goNextCharacter(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the document window.
        """
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break
        if obj:
            self.setCaretPosition(obj, characterOffset)
        else:
            self.clearCaretContext()

        self.updateBraille(obj)
        self.speakCharacterAtOffset(obj, characterOffset)

    def goPreviousCharacter(self, inputEvent):
        """Positions the caret offset to the previous character or object
        in the document window.
        """
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.findPreviousCaretInOrder(
                obj, characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break

        if obj:
            self.setCaretPosition(obj, characterOffset)
        else:
            self.clearCaretContext()

        self.updateBraille(obj)
        self.speakCharacterAtOffset(obj, characterOffset)

    def goPreviousWord(self, inputEvent):
        """Positions the caret offset to beginning of the previous
        word or object in the document window.
        """

        # Find the beginning of the current word
        #
        [obj, characterOffset] = self.getCaretContext()
        contents = self.getWordContentsAtOffset(obj, characterOffset)
        [obj, startOffset, endOffset] = contents[0]

        # Now go to the beginning of the previous word
        #
        [obj, characterOffset] = self.findPreviousCaretInOrder(obj,
                                                               startOffset)
        contents = self.getWordContentsAtOffset(obj, characterOffset)

        if not len(contents):
            return

        [obj, startOffset, endOffset] = contents[0]

        self.setCaretPosition(obj,  startOffset)
        self.updateBraille(obj)
        self.speakContents(self.getWordContentsAtOffset(obj, startOffset))

    def goNextWord(self, inputEvent):
        """Positions the caret offset to the end of next word or object
        in the document window.
        """

        # Find the beginning of the current word
        #
        [obj, characterOffset] = self.getCaretContext()
        contents = self.getWordContentsAtOffset(obj, characterOffset)
        [obj, startOffset, endOffset] = contents[0]

        # Now go to the beginning of the next word.
        #
        [obj, characterOffset] = self.findNextCaretInOrder(obj, endOffset - 1)
        contents = self.getWordContentsAtOffset(obj, characterOffset)

        if not len(contents):
            return

        [obj, startOffset, endOffset] = contents[0]

        # [[[TODO: WDW - to be more like gedit, we should position the
        # caret just after the last character of the word.]]]
        #
        self.setCaretPosition(obj,  startOffset)
        self.updateBraille(obj)
        self.speakContents(self.getWordContentsAtOffset(obj, startOffset))

    def altFindPreviousLine(self, obj, characterOffset):
        """Locates the caret offset at the previous line in the document
        window.

        Arguments:
        -obj:             the object from which the search should begin
        -characterOffset: the offset within obj from which the search should
                          begin

        Returns the [obj, characterOffset] at the beginning of the line.
        """

        if not obj:
            [obj, characterOffset] = self.getCaretContext()

        if not obj:
            return self.getTopOfFile()

        currentLine = self._currentLineContents
        index = self.findObjectOnLine(obj, characterOffset, currentLine)
        if index < 0:
            currentLine = self.getLineContentsAtOffset(obj, characterOffset)

        [prevObj, prevOffset] = \
            self.findPreviousCaretInOrder(currentLine[0][0], currentLine[0][1])

        # We need to be sure that we've actually found a new line rather than
        # a space at the end of the current line.
        #
        text = self.queryNonEmptyText(prevObj)
        if text:
            line = text.getTextAfterOffset(prevOffset,
                                           pyatspi.TEXT_BOUNDARY_LINE_START)
            if not len(line[0].strip()) \
                   and prevObj.getRole() != pyatspi.ROLE_ENTRY:
                [prevObj, prevOffset] = \
                          self.findPreviousCaretInOrder(prevObj, prevOffset)
            else:
                prevOffset = line[1]

        # If the user did some back-to-back arrowing, we might already have
        # the line contents.
        #
        prevLine = self._previousLineContents
        index = self.findObjectOnLine(prevObj, prevOffset, prevLine)
        if index < 0:
            prevLine = self.getLineContentsAtOffset(prevObj, prevOffset)
    
        if not prevLine:
            return [None, -1]

        prevObj = prevLine[0][0]
        prevOffset = prevLine[0][1]

        # Dealing with things like nested tables from the right side is hard.
        # For now, I'm going to look at the previous caret in order.  If it's
        # on the same line, we'll give it another go.  In testing, we usually
        # get it right the first time so this shouldn't be too much of a hit.
        #
        [testObj, testOffset] = self.findPreviousCaretInOrder(prevObj,
                                                              prevOffset)
        extents1 = self.getExtents(prevObj, prevOffset, prevOffset + 1)
        extents2 = self.getExtents(testObj, testOffset, testOffset + 1)
        if self.onSameLine(extents1, extents2):
            #print "previous line failed"
            prevLine = self.getLineContentsAtOffset(testObj, testOffset)
            if not prevLine:
                return [None, -1]

            prevObj = prevLine[0][0]
            prevOffset = prevLine[0][1]

        if currentLine == prevLine:
            # For some reason we're stuck.
            #
            #print "find prev line failed"
            prevObj = self.findPreviousObject(prevObj)
            prevOffset = 0
            prevLine = self.getLineContentsAtOffset(prevObj, prevOffset)
            if currentLine == prevLine:
                # print "find prev line still stuck"
                prevObj = self.findPreviousObject(prevObj)
                prevLine = self.getLineContentsAtOffset(prevObj, prevOffset)

        [prevObj, prevOffset] = self.findNextCaretInOrder(prevObj, 
                                                          prevOffset - 1)

        if not arrowToLineBeginning:
            extents = self.getExtents(obj, 
                                      characterOffset, 
                                      characterOffset + 1)
            oldX = extents[0]
            for item in prevLine:
                extents = self.getExtents(item[0], item[1], item[2])
                newX1 = extents[0]
                newX2 = newX1 + extents[2]
                if newX1 <= oldX <= newX2:
                    prevObj = item[0]
                    prevOffset = 0
                    text = self.queryNonEmptyText(prevObj)
                    if text:
                        newY = extents[1] + extents[3] / 2
                        prevOffset = text.getOffsetAtPoint(oldX, newY, 0)
                    break

        self._nextLineContents = self._currentLineContents
        self._currentLineContents = prevLine

        return [prevObj, prevOffset]

    def findPreviousLine(self, obj, characterOffset):
        """Locates the caret offset at the previous line in the document
        window, attempting to preserve horizontal caret position.

        Arguments:
        -obj:             the object from which the search should begin
        -characterOffset: the offset within obj from which the search should
                          begin

        Returns the [obj, characterOffset] at which to position the caret.
        """

        if useNewLineNav:
            [prevObj, prevOffset] = self.altFindPreviousLine(obj,
                                                             characterOffset)
            return [prevObj, prevOffset]

        lineExtents = self.getExtents(
            obj, characterOffset, characterOffset + 1)
        try:
            characterExtents = self.targetCharacterExtents
        except:
            characterExtents = lineExtents

        #print "FPL STARTING AT", obj.getRole(), characterOffset

        crossedLineBoundary = False
        [lastObj, lastCharacterOffset] = [obj, characterOffset]
        while obj:
            extents = self.getExtents(
                obj, characterOffset, characterOffset + 1)
            text = self.queryNonEmptyText(obj)
            if text:
                if characterOffset > 0:
                    previousChar = \
                        text.getText(characterOffset - 1, characterOffset)
                else:
                    previousChar = None
                currentChar = text.getText(characterOffset,
                                           characterOffset + 1)
            else:
                previousChar = None
                currentChar = None

            #print "FPL LOOKING AT", obj.getRole(), extents

            # Sometimes the reported width and/or height of a character
            # is a large negative number.  When that occurs, we want to
            # ignore that character.
            #
            validExtents = True
            if (extents[2] < 0) or (extents[3] < 0):
                validExtents = False

            # [[[TODO: WDW - HACK.  I think we end up with a zero
            # sized character when the accessible text implementation
            # of Gecko gives us whitespace that is not visible, but
            # is in the raw HTML source.  This should hopefully be
            # fixed at some point, but we just ignore it for now.
            #
            if validExtents and extents != (0, 0, 0, 0):
                if not self.onSameLine(extents, lineExtents):
                    if not crossedLineBoundary:
                        if currentChar != "\n" and extents[1] >= 0:
                            crossedLineBoundary = True
                        elif previousChar == "\n":
                            crossedLineBoundary = True
                        elif obj.getRole() == pyatspi.ROLE_ENTRY:
                            crossedLineBoundary = True
                        if crossedLineBoundary:
                            lineExtents = extents
                    else:
                        break
                elif crossedLineBoundary \
                     and (extents[0] <= characterExtents[0]):
                    break
                else:
                    lineExtents = self.getBoundary(lineExtents, extents)

                [lastObj, lastCharacterOffset] = [obj, characterOffset]

            [obj, characterOffset] = \
                  self.findPreviousCaretInOrder(obj, characterOffset)

        #print "FPL ENDED UP AT", lastObj.getRole(), lineExtents

        contents = self.getLineContentsAtOffset(lastObj,
                                                lastCharacterOffset)

        if not len(contents):
            return

        if arrowToLineBeginning:
            [lastObj, lastCharacterOffset, endOffset] = contents[0]
            # [[[TODO: JD - HACK. Our work-around for the problem of
            # list numbers/bullets having extents of (0, 0, 0, 0) means
            # that lastCharacterOffset is the unfocusable number/bullet.
            # Move back to the first character in the list before setting
            # the caret position.
            #
            if lastObj.getRole() == pyatspi.ROLE_LIST_ITEM and not \
               lastObj.getState().contains(pyatspi.STATE_FOCUSABLE):
                extents = self.getExtents(lastObj,
                                          lastCharacterOffset,
                                          lastCharacterOffset + 1)
                while extents == (0, 0, 0, 0):
                    lastCharacterOffset += 1
                    extents = self.getExtents(lastObj,
                                              lastCharacterOffset,
                                              lastCharacterOffset + 1)

        return [lastObj, lastCharacterOffset]

    def altFindNextLine(self, obj, characterOffset):
        """Locates the caret offset at the next line in the document
        window.

        Arguments:
        -obj:             the object from which the search should begin
        -characterOffset: the offset within obj from which the search should
                          begin

        Returns the [obj, characterOffset] at the beginning of the line.
        """

        if not obj:
            [obj, characterOffset] = self.getCaretContext()

        if not obj:
            return self.getBottomOfFile()

        currentLine = self._currentLineContents
        index = self.findObjectOnLine(obj, characterOffset, currentLine)
        if index < 0:
            currentLine = self.getLineContentsAtOffset(obj, characterOffset)

        [nextObj, nextOffset] = self.findNextCaretInOrder(currentLine[-1][0],
                                                          currentLine[-1][2])

        # We need to be sure that we've actually found a new line rather than
        # a space at the end of the current line.
        #
        text = self.queryNonEmptyText(nextObj)
        if text:
            line = text.getTextAfterOffset(nextOffset,
                                           pyatspi.TEXT_BOUNDARY_LINE_START)
            if not len(line[0].strip()) \
               and nextObj.getRole() != pyatspi.ROLE_ENTRY:
                [nextObj, nextOffset] = \
                          self.findNextCaretInOrder(nextObj, nextOffset)
            else:
                nextOffset = line[1]

        # If the user did some back-to-back arrowing, we might already have
        # the line contents.
        #
        nextLine = self._nextLineContents
        index = self.findObjectOnLine(nextObj, nextOffset, nextLine)
        if index < 0:
            nextLine = self.getLineContentsAtOffset(nextObj, nextOffset)

        if not nextLine:
            return [None, -1]

        elif currentLine == nextLine:
            # For some reason we're stuck.
            #
            # print "find next line failed"
            nextObj = self.findNextObject(nextObj)
            nextOffset = 0
            nextLine = self.getLineContentsAtOffset(nextObj, nextOffset)
            if currentLine == nextLine:
                # print "find next line still stuck"
                nextObj = self.findNextObject(nextObj)
                nextLine = self.getLineContentsAtOffset(nextObj, nextOffset)

        if not arrowToLineBeginning:
            extents = self.getExtents(obj,
                                      characterOffset, 
                                      characterOffset + 1)
            oldX = extents[0]
            for item in nextLine:
                extents = self.getExtents(item[0], item[1], item[2])
                newX1 = extents[0]
                newX2 = newX1 + extents[2]
                if newX1 <= oldX <= newX2:
                    nextObj = item[0]
                    nextOffset = 0
                    text = self.queryNonEmptyText(nextObj)
                    if text:
                        newY = extents[1] + extents[3] / 2
                        nextOffset = text.getOffsetAtPoint(oldX, newY, 0)
                    break

        self._previousLineContents = self._currentLineContents
        self._currentLineContents = nextLine

        return [nextObj, nextOffset]

    def findNextLine(self, obj, characterOffset):
        """Locates the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.

        Arguments:
        -obj:             the object from which the search should begin
        -characterOffset: the offset within obj from which the search should
                          begin

        Returns the [obj, characterOffset] at which to position the caret.
        """

        if useNewLineNav:
            [nextObj, nextOffset] = self.altFindNextLine(obj, characterOffset)
            return nextObj, nextOffset

        lineExtents = self.getExtents(
            obj, characterOffset, characterOffset + 1)
        try:
            characterExtents = self.targetCharacterExtents
        except:
            characterExtents = lineExtents

        #print "FNL STARTING AT", obj.getRole(), characterOffset

        crossedLineBoundary = False
        [lastObj, lastCharacterOffset] = [obj, characterOffset]
        while obj:
            extents = self.getExtents(
                obj, characterOffset, characterOffset + 1)
            text = self.queryNonEmptyText(obj)
            if text:
                if characterOffset > 0:
                    previousChar = \
                        text.getText(characterOffset - 1, characterOffset)
                else:
                    previousChar = None
                currentChar = \
                        text.getText(characterOffset, characterOffset + 1)
            else:
                previousChar = None
                currentChar = None

            #print "FNL LOOKING AT", obj.getRole(), extents

            # Sometimes the reported width and/or height of a character
            # is a large negative number.  When that occurs, we want to
            # ignore that character.
            #
            validExtents = True
            if (extents[2] < 0) or (extents[3] < 0):
                validExtents = False

            # [[[TODO: WDW - HACK.  I think we end up with a zero
            # sized character when the accessible text implementation
            # of Gecko gives us whitespace that is not visible, but
            # is in the raw HTML source.  This should hopefully be
            # fixed at some point, but we just ignore it for now.]]]
            #
            if validExtents and extents != (0, 0, 0, 0):
                if not self.onSameLine(extents, lineExtents):
                    if not crossedLineBoundary:
                        if currentChar != "\n" and extents[1] >= 0:
                            crossedLineBoundary = True
                        elif previousChar == "\n":
                            crossedLineBoundary = True
                        elif obj.getRole() == pyatspi.ROLE_ENTRY:
                            crossedLineBoundary = True
                        if crossedLineBoundary:
                            lineExtents = extents
                            if arrowToLineBeginning:
                                [lastObj, lastCharacterOffset] = \
                                    [obj, characterOffset]
                                break
                    else:
                        break
                elif crossedLineBoundary \
                     and (extents[0] >= characterExtents[0]):
                    break
                else:
                    lineExtents = self.getBoundary(extents, lineExtents)

                [lastObj, lastCharacterOffset] = [obj, characterOffset]

            [obj, characterOffset] = \
                  self.findNextCaretInOrder(obj, characterOffset)

        return [lastObj, lastCharacterOffset]

    def goPreviousLine(self, inputEvent):
        """Positions the caret offset at the previous line in the document
        window, attempting to preserve horizontal caret position.
        """
        [obj, characterOffset] = self.getCaretContext()
        [previousObj, previousCharOffset] = \
                                   self.findPreviousLine(obj, characterOffset)
        if not previousObj:
            return

        self.setCaretPosition(previousObj, previousCharOffset)
        self.presentLine(previousObj, previousCharOffset)

        # Debug...
        #
        #contents = self.getLineContentsAtOffset(previousObj,
        #                                        previousCharOffset)
        #self.dumpContents(inputEvent, contents)

    def goNextLine(self, inputEvent):
        """Positions the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.
        """

        [obj, characterOffset] = self.getCaretContext()
        [nextObj, nextCharOffset] = self.findNextLine(obj, characterOffset)

        if not nextObj:
            return

        self.setCaretPosition(nextObj, nextCharOffset)
        self.presentLine(nextObj, nextCharOffset)

        # Debug...
        #
        #contents = self.getLineContentsAtOffset(nextObj, nextCharOffset)
        #self.dumpContents(inputEvent, contents)

    def goTopOfFile(self, inputEvent):
        """Positions the caret offset at the beginning of the document."""

        [obj, characterOffset] = self.getTopOfFile()
        self.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def goBottomOfFile(self, inputEvent):
        """Positions the caret offset at the end of the document."""

        [obj, characterOffset] = self.getBottomOfFile()
        self.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def expandComboBox(self, inputEvent):
        """If focus is on a menu item, but the containing combo box does not
        have focus, give the combo box focus and expand it.  Note that this
        is necessary because with Orca controlling the caret it is possible
        to arrow to a menu item within the combo box without actually giving
        the containing combo box focus.
        """

        [obj, characterOffset] = self.getCaretContext()
        comboBox = None
        if obj.getRole() == pyatspi.ROLE_MENU_ITEM:
            comboBox = self.getAncestor(obj,
                                        [pyatspi.ROLE_COMBO_BOX],
                                        [pyatspi.ROLE_DOCUMENT_FRAME])
        else:
            index = self.getChildIndex(obj, characterOffset)
            if index >= 0:
                comboBox = obj[index]

        if not comboBox:
            return

        try:
            action = comboBox.queryAction()
        except:
            pass
        else:
            orca.setLocusOfFocus(None, comboBox)
            comboBox.queryComponent().grabFocus()
            for i in range(0, action.nActions):
                name = action.getName(i)
                if name == "open":
                    action.doAction(i)
                    break

    def goPreviousHeading(self, inputEvent):
        """Go to the previous heading regardless of level."""
        wrap = True
        [obj, wrapped] = self.findPreviousRole([pyatspi.ROLE_HEADING], wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is in reference to navigating HTML content
            # by heading (e.g., <h1>).
            #
            speech.speak(_("No more headings."))

    def goNextHeading(self, inputEvent):
        """Go to the next heading regardless of level."""
        wrap = True
        [obj, wrapped] = self.findNextRole([pyatspi.ROLE_HEADING], wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is in reference to navigating HTML content
            # by heading (e.g., <h1>).
            #
            speech.speak(_("No more headings."))

    def goPreviousHeadingAtLevel(self, inputEvent, desiredLevel):
        """Go to the previous heading at the specified level.

        Arguments:
        - desiredLevel: the level (1-6) of the heading to locate
        """
        
        found = False
        level = 0
        [obj, characterOffset] = self.getCaretContext()
        if obj.parent.getRole() == pyatspi.ROLE_HEADING:
            obj = obj.parent
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findPreviousRole([pyatspi.ROLE_HEADING], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False
            if obj:
                level = self.getHeadingLevel(obj)
                if level == desiredLevel:
                    found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is in reference to navigating HTML content
            # by heading (e.g., <h1>).
            #
            speech.speak(_("No more headings at level %d.") % desiredLevel)

    def goNextHeadingAtLevel(self, inputEvent, desiredLevel):
        """Go to the next heading at the specified level.

        Arguments:
        - desiredLevel: the level (1-6) of the heading to locate
        """

        found = False
        level = 0
        [obj, characterOffset] = self.getCaretContext()
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findNextRole([pyatspi.ROLE_HEADING], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False
            if obj:
                level = self.getHeadingLevel(obj)
                if level == desiredLevel:
                    found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is in reference to navigating HTML content
            # by heading (e.g., <h1>).
            #
            speech.speak(_("No more headings at level %d.") % desiredLevel)

    def goNextHeading1(self, inputEvent):
        """Go to the next heading at the level 1."""
        self.goNextHeadingAtLevel(inputEvent, 1)

    def goPreviousHeading1(self, inputEvent):
        """Go to the previous heading at the level 1."""
        self.goPreviousHeadingAtLevel(inputEvent, 1)

    def goNextHeading2(self, inputEvent):
        """Go to the next heading at the level 2."""
        self.goNextHeadingAtLevel(inputEvent, 2)

    def goPreviousHeading2(self, inputEvent):
        """Go to the previous heading at the level 2."""
        self.goPreviousHeadingAtLevel(inputEvent, 2)

    def goNextHeading3(self, inputEvent):
        """Go to the next heading at the level 3."""
        self.goNextHeadingAtLevel(inputEvent, 3)

    def goPreviousHeading3(self, inputEvent):
        """Go to the previous heading at the level 3."""
        self.goPreviousHeadingAtLevel(inputEvent, 3)

    def goNextHeading4(self, inputEvent):
        """Go to the next heading at the level 4."""
        self.goNextHeadingAtLevel(inputEvent, 4)

    def goPreviousHeading4(self, inputEvent):
        """Go to the previous heading at the level 4."""
        self.goPreviousHeadingAtLevel(inputEvent, 4)

    def goNextHeading5(self, inputEvent):
        """Go to the next heading at the level 5."""
        self.goNextHeadingAtLevel(inputEvent, 5)

    def goPreviousHeading5(self, inputEvent):
        """Go to the previous heading at the level 5."""
        self.goPreviousHeadingAtLevel(inputEvent, 5)

    def goNextHeading6(self, inputEvent):
        """Go to the next heading at the level 6."""
        self.goNextHeadingAtLevel(inputEvent, 6)

    def goPreviousHeading6(self, inputEvent):
        """Go to the previous heading at the level 6."""
        self.goPreviousHeadingAtLevel(inputEvent, 6)

    def goPreviousChunk(self, inputEvent):
        """Go to the previous chunk/large object."""
        wrap = True
        [obj, wrapped] = self.findPrevByPredicate(self.__matchChunk, wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML in a structural
            # manner, where a 'large object' is a logical chunk of
            # text, such as a paragraph, a list, a table, etc.
            #
            speech.speak(_("No more large objects."))

    def goNextChunk(self, inputEvent):
        """Go to the next chunk/large object."""
        wrap = True
        [obj, wrapped] = self.findNextByPredicate(self.__matchChunk, wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML in a structural
            # manner, where a 'large object' is a logical chunk of
            # text, such as a paragraph, a list, a table, etc.
            #
            speech.speak(_("No more large objects."))

    def goPreviousLandmark(self, inputEvent):
        wrap = True
        [obj, wrapped] = self.findPrevByPredicate(self.__matchLandmark, wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating to the previous ARIA
            # role landmark.  ARIA role landmarks are the W3C defined HTML 
            # tag attribute 'role' used to identify important part of 
            # webpage like banners, main context, search etc.  This is an 
            # that one was not found.
            #
            speech.speak(_("No landmark found."))

    def goNextLandmark(self, inputEvent):
        wrap = True
        [obj, wrapped] = self.findNextByPredicate(self.__matchLandmark, wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating to the next ARIA
            # role landmark. This is an that one was not found.
            #
            speech.speak(_("No landmark found."))

    def goPreviousObjectInOrder(self, inputEvent):
        """Go to the previous object in order, regardless of type or size."""

        [obj, characterOffset] = self.getCaretContext()

        # Work our way out of form lists and combo boxes.
        #
        if obj and obj.getState().contains(pyatspi.STATE_SELECTABLE):
            obj = obj.parent.parent
            characterOffset = self.getCharacterOffsetInParent(obj)
            self._currentLineContents = None

        characterOffset = max(0, characterOffset)
        [prevObj, prevOffset] = [obj, characterOffset]
        found = False
        mayHaveGoneTooFar = False

        line = self._currentLineContents \
               or self.getLineContentsAtOffset(obj, characterOffset)

        while line and not found:
            useful = self.getMeaningfulObjectsFromLine(line)
            index = self.findObjectOnLine(prevObj, prevOffset, useful)
            if not self.isSameObject(obj, prevObj):
                # We have found a different object (e.g. text before the
                # current link). 
                #
                prevObj = useful[-1][0]
                prevOffset = useful[-1][1]
                # The question is, have we found the beginning of this 
                # object?  If the offset is 0 or there's more than one object
                # on this line it's safe to assume we've found the beginning.
                #
                found = (prevOffset == 0 or len(useful) > 1)
                # Otherwise, we won't know for certain until we've gone
                # to the line(s) before this one and found a different
                # object, at which point we may have gone too far.
                #
                if not found:
                    mayHaveGoneTooFar = True
                    obj = prevObj
                    characterOffset = prevOffset

            elif 0 < index < len(useful):
                prevObj = useful[index - 1][0]
                prevOffset = useful[index - 1][1]
                found = True

            if not found:
                self._nextLineContents = line
                [prevObj, prevOffset] = self.findPreviousLine(line[0][0], 
                                                              line[0][1])
                line = self._currentLineContents
                if self._currentLineContents == self._nextLineContents:
                    break

        if not found:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
            [prevObj, prevOffset] = self.getBottomOfFile()
            line = self.getLineContentsAtOffset(prevObj, prevOffset)
            useful = self.getMeaningfulObjectsFromLine(line)
            if useful:
                prevObj = useful[-1][0]
                prevOffset = useful[-1][1]
            found = not (prevObj is None)

        elif mayHaveGoneTooFar and self._nextLineContents:
            if not self.isSameObject(obj, prevObj):
                line = self._nextLineContents
                prevObj = line[0][0]
                prevOffset = line[0][1]

        if found:
            self._currentLineContents = line
            self.setCaretPosition(prevObj, prevOffset)
            self.updateBraille(prevObj)
            objectContents = self.getObjectContentsAtOffset(prevObj,
                                                            prevOffset)
            objectContents = [objectContents[0]]
            self.speakContents(objectContents)

    def goNextObjectInOrder(self, inputEvent):
        """Go to the next object in order, regardless of type or size."""

        [obj, characterOffset] = self.getCaretContext()

        # Work our way out of form lists and combo boxes.
        #
        if obj and obj.getState().contains(pyatspi.STATE_SELECTABLE):
            obj = obj.parent.parent
            characterOffset = self.getCharacterOffsetInParent(obj)
            self._currentLineContents = None

        characterOffset = max(0, characterOffset)
        [nextObj, nextOffset] = [obj, characterOffset]
        found = False

        line = self._currentLineContents \
               or self.getLineContentsAtOffset(obj, characterOffset)

        while line and not found:
            useful = self.getMeaningfulObjectsFromLine(line)
            index = self.findObjectOnLine(nextObj, nextOffset, useful)
            if not self.isSameObject(obj, nextObj):
                nextObj = useful[0][0]
                nextOffset = useful[0][1]
                found = True
            elif 0 <= index < len(useful) - 1:
                nextObj = useful[index + 1][0]
                nextOffset = useful[index + 1][1]
                found = True
            else:
                self._previousLineContents = line
                [nextObj, nextOffset] = self.findNextLine(line[-1][0], 
                                                          line[-1][2])
                line = self._currentLineContents
                if self._currentLineContents == self._previousLineContents:
                    break

        if not found:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
            [nextObj, nextOffset] = self.getTopOfFile()
            line = self.getLineContentsAtOffset(nextObj, nextOffset)
            useful = self.getMeaningfulObjectsFromLine(line)
            if useful:
                nextObj = useful[0][0]
                nextOffset = useful[0][1]
            found = not (nextObj is None)

        if found:
            self._currentLineContents = line
            self.setCaretPosition(nextObj, nextOffset)
            self.updateBraille(nextObj)
            objectContents = self.getObjectContentsAtOffset(nextObj,
                                                            nextOffset)
            objectContents = [objectContents[0]]
            self.speakContents(objectContents)

    def goPreviousList(self, inputEvent):
        """Go to the previous (un)ordered list."""
        [obj, characterOffset] = self.getCaretContext()
        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findPreviousRole([pyatspi.ROLE_LIST], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False

            # We need to be sure that the list in question is an (un)ordered
            # list rather than a list in a form field. Form field lists are
            # focusable; (un)ordered lists are not.
            #
            if obj and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                found = True

        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj and found:
            nItems = 0
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LIST_ITEM:
                    nItems += 1
            # Translators: this represents a list in HTML.
            #
            itemString = ngettext("List with %d item",
                                  "List with %d items",
                                  nItems) % nItems
            speech.speak(itemString)
            nestingLevel = 0
            parent = obj.parent
            while parent.getRole() == pyatspi.ROLE_LIST:
                nestingLevel += 1
                parent = parent.parent
            if nestingLevel:
                # Translators: this represents a list item in HTML.
                # The nesting level is how 'deep' the item is (e.g.,
                # a level of 2 represents a list item inside a list
                # that's inside another list).
                #
                speech.speak(_("Nesting level %d") % nestingLevel)
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)

        else:
            # Translators: this is for navigating HTML content by moving
            # from bulleted/numbered list to bulleted/numbered list.
            #
            speech.speak(_("No more lists."))

    def goNextList(self, inputEvent):
        """Go to the next (un)ordered list."""
        [obj, characterOffset] = self.getCaretContext()
        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findNextRole([pyatspi.ROLE_LIST], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False

            # We need to be sure that the list in question is an (un)ordered
            # list rather than a list in a form field. Form field lists are
            # focusable; (un)ordered lists are not.
            #
            if obj and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj and found:
            nItems = 0
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LIST_ITEM:
                    nItems += 1
            # Translators: this represents a list in HTML.
            #
            itemString = ngettext("List with %d item",
                                  "List with %d items",
                                  nItems) % nItems
            speech.speak(itemString)
            nestingLevel = 0
            parent = obj.parent
            while parent.getRole() == pyatspi.ROLE_LIST:
                nestingLevel += 1
                parent = parent.parent
            if nestingLevel:
                # Translators: this represents a list item in HTML.
                # The nesting level is how 'deep' the item is (e.g.,
                # a level of 2 represents a list item inside a list
                # that's inside another list).
                #
                speech.speak(_("Nesting level %d") % nestingLevel)
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)

        else:
            # Translators: this is for navigating HTML content by moving
            # from bulleted/numbered list to bulleted/numbered list.
            #
            speech.speak(_("No more lists."))

    def goPreviousListItem(self, inputEvent):
        """Go to the previous item in an (un)ordered list."""
        [obj, characterOffset] = self.getCaretContext()
        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findPreviousRole([pyatspi.ROLE_LIST_ITEM], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False

            # We need to be sure that the list item in question is the child
            # of an (un)ordered list rather than a list in a form field.
            # Form field list items are focusable; (un)ordered list items are
            # not.
            #
            if obj and \
               not (obj.getState().contains(pyatspi.STATE_FOCUSABLE)):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is for navigating HTML content by
            # moving from bulleted/numbered list item to
            # bulleted/numbered list item.
            #
            speech.speak(_("No more list items."))

    def goNextListItem(self, inputEvent):
        """Go to the next item in an (un)ordered list."""
        [obj, characterOffset] = self.getCaretContext()
        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findNextRole([pyatspi.ROLE_LIST_ITEM], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False

            # We need to be sure that the list item in question is the child
            # of an (un)ordered list rather than a list in a form field.
            # Form field list items are focusable; (un)ordered list items are
            # not.
            #
            if obj and \
               not (obj.getState().contains(pyatspi.STATE_FOCUSABLE)):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is for navigating HTML content by
            # moving from bulleted/numbered list item to
            # bulleted/numbered list item.
            #
            speech.speak(_("No more list items."))

    def goPreviousUnvisitedLink(self, inputEvent):
        """Go to the previous unvisited link."""

        # If the currentObject has a link in its ancestry, we've
        # already started out on a link and need to move off of
        # it else we'll get stuck.
        #
        [obj, characterOffset] = self.getCaretContext()
        containingLink = self.getAncestor(obj,
                                          [pyatspi.ROLE_LINK],
                                          [pyatspi.ROLE_DOCUMENT_FRAME])
        if containingLink:
            obj = containingLink

        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findPreviousRole([pyatspi.ROLE_LINK], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False
            if obj and \
               not obj.getState().contains(pyatspi.STATE_VISITED):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML content by
            # moving from link to link.
            #
            speech.speak(_("No more unvisited links."))

    def goNextUnvisitedLink(self, inputEvent):
        """Go to the next unvisited link."""
        [obj, characterOffset] = self.getCaretContext()
        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findNextRole([pyatspi.ROLE_LINK], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False
            if obj and \
               not obj.getState().contains(pyatspi.STATE_VISITED):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML content by
            # moving from link to link.
            #
            speech.speak(_("No more unvisited links."))

    def goPreviousVisitedLink(self, inputEvent):
        """Go to the previous visited link."""

        # If the currentObject has a link in its ancestry, we've
        # already started out on a link and need to move off of
        # it else we'll get stuck.
        #
        [obj, characterOffset] = self.getCaretContext()
        containingLink = self.getAncestor(obj,
                                          [pyatspi.ROLE_LINK],
                                          [pyatspi.ROLE_DOCUMENT_FRAME])
        if containingLink:
            obj = containingLink

        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findPreviousRole([pyatspi.ROLE_LINK], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False
            if obj and \
               obj.getState().contains(pyatspi.STATE_VISITED):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML content by
            # moving from link to link.
            #
            speech.speak(_("No more visited links."))

    def goNextVisitedLink(self, inputEvent):
        """Go to the next visited link."""
        [obj, characterOffset] = self.getCaretContext()
        found = False
        wrap = True
        while obj and not found:
            [obj, wrapped] = \
                  self.findNextRole([pyatspi.ROLE_LINK], wrap, obj)
            # We should only wrap if we haven't already done so.
            #
            if wrapped:
                wrap = False

            if obj and \
               obj.getState().contains(pyatspi.STATE_VISITED):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj and found:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML content by
            # moving from link to link.
            #
            speech.speak(_("No more visited links."))

    def goPreviousBlockquote(self, inputEvent):
        """Go to the previous blockquote."""

        # If the current object has a blockquote in its ancestry, we
        # need to move out of it else we'll get stuck.
        #
        [obj, characterOffset] = self.getCaretContext()
        candidate = obj
        while candidate and (candidate != candidate.parent) and \
              (candidate.getRole() != pyatspi.ROLE_DOCUMENT_FRAME):
            if self.isBlockquote(candidate):
                obj = candidate
                break
            else:
                candidate = candidate.parent
        currentObj = obj
        found = False
        wrapped = False
        wrap = True
        while obj and not found:
            obj = self.findPreviousObject(obj)
            if not obj and wrap and not wrapped:
                obj = self.getLastObject()
                wrapped = True
            if obj and self.isBlockquote(obj) and \
               not self.isSameObject(currentObj, obj):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is for navigating HTML content by
            # moving from blockquote to blockquote.
            #
            speech.speak(_("No more blockquotes."))

    def goNextBlockquote(self, inputEvent):
        """Go to the next blockquote."""
        [obj, characterOffset] = self.getCaretContext()
        currentObj = obj
        found = False
        wrapped = False
        wrap = True
        while obj and not found:
            obj = self.findNextObject(obj)
            if not obj and wrap and not wrapped:
                documentFrame = self.getDocumentFrame()
                obj = documentFrame[0]
                wrapped = True
            if obj and self.isBlockquote(obj) and \
               not self.isSameObject(currentObj, obj):
                found = True
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLine(obj, characterOffset)
        else:
            # Translators: this is for navigating HTML content by
            # moving from blockquote to blockquote.
            #
            speech.speak(_("No more blockquotes."))

    def goPreviousFormField(self, inputEvent):
        """Go to the previous form field."""

        # If the current object is a list item in a form field, we
        # need to move up to the parent list before we search
        # for the previous list; otherwise we'll find the current
        # list first.
        #
        [obj, characterOffset] = self.getCaretContext()
        currentObj = obj
        if obj.getRole() == pyatspi.ROLE_LIST_ITEM and \
           obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            obj = obj.parent

        found = False
        wrapped = False
        wrap = True
        while obj and not found:
            obj = self.findPreviousObject(obj)
            if not obj and wrap and not wrapped:
                obj = self.getLastObject()
                wrapped = True
            if obj:
                # For performance purposes, we do not want to work
                # our way up through list items in search of the
                # parent list.
                #
                if obj.getRole() == pyatspi.ROLE_LIST_ITEM:
                    obj = obj.parent
                found = self.isFormField(obj)
                if wrapped and self.isSameObject(currentObj, obj):
                    obj = None
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            # We actively avoid grabbing focus on lists in HTML forms
            # in setCaretPosition() so that a user doesn't accidentally
            # arrow into one and change its value.  Here we actually
            # do want to grab focus should we be on a list or combo box.
            #
            if obj.getRole() in [pyatspi.ROLE_LIST, pyatspi.ROLE_COMBO_BOX]:
                obj.queryComponent().grabFocus()
            else:
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents(self.getObjectContentsAtOffset(obj,
                                                             characterOffset))
        else:
            # Translators: this is for navigating HTML content by
            # moving from form field to form field.
            #
            speech.speak(_("No more form fields."))

    def goNextFormField(self, inputEvent):
        """Go to the next form field."""
        [obj, characterOffset] = self.getCaretContext()
        currentObj = obj
        found = False
        wrapped = False
        wrap = True
        # For performance purposes, we do not want to examine each item
        # in the current combo box or list via findNextObject.
        #
        if obj.getRole() == pyatspi.ROLE_LIST_ITEM \
           and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            obj = obj.parent
        if obj.getRole() == pyatspi.ROLE_LIST \
           and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            obj = obj[obj.childCount - 1]
        elif obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            menu = obj[0]
            obj = menu[menu.childCount - 1]

        while obj and not found:
            obj = self.findNextObject(obj)
            if not obj and wrap and not wrapped:
                documentFrame = self.getDocumentFrame()
                obj = documentFrame[0]
                wrapped = True
            if obj:
                found = self.isFormField(obj)
                if wrapped and self.isSameObject(currentObj, obj):
                    obj = None
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)

            # We actively avoid grabbing focus on lists in HTML forms
            # in setCaretPosition() so that a user doesn't accidentally
            # arrow into one and change its value.  Here we actually
            # do want to grab focus should we be on a list or combo box.
            #
            if obj.getRole() in [pyatspi.ROLE_LIST, pyatspi.ROLE_COMBO_BOX]:
                obj.queryComponent().grabFocus()
            else:
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents(self.getObjectContentsAtOffset(obj,
                                                             characterOffset))
        else:
            # Translators: this is for navigating HTML content by
            # moving from form field to form field.
            #
            speech.speak(_("No more form fields."))

    def moveToCell(self, obj):
        """Move to the specified cell in an HTML table.

        Arguments:
        - obj: the table cell to move to.
        """
        spanString = self.getCellSpanInfo (obj)
        blank = self.isBlankCell(obj)
        [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
        self.setCaretPosition(obj, characterOffset)
        self.updateBraille(obj)
        if not blank:
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                             characterOffset))
        else:
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            speech.speak(_("blank"))

        if speakCellCoordinates:
            [row, col] = self.getCellCoordinates(obj)
            # Translators: this represents the (row, col) position of
            # a cell in a table.
            #
            speech.speak(_("Row %d, column %d.") % (row + 1, col + 1))

        if spanString and speakCellSpan:
            speech.speak(spanString)

    def goPreviousTable(self, inputEvent):
        """Go to the previous table."""
        wrap = True
        [obj, wrapped] = self.findPreviousRole([pyatspi.ROLE_TABLE], wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
        if obj:
            table = obj.queryTable()
            caption = self.getTableCaption(obj)
            if self.queryNonEmptyText(caption):
                text = self.getDisplayedText(caption)
                speech.speak(text)
            nonUniformString = ""
            nonUniform = self.isNonUniformTable(obj)
            if nonUniform:
                # Translators: a uniform table is one in which each table
                # cell occupies one row and one column (i.e. a perfect grid)
                # In contrast, a non-uniform table is one in which at least
                # one table cell occupies more than one row and/or column.
                #
                nonUniformString = _("Non-uniform")
            nRows = table.nRows
            nColumns = table.nColumns
            # Translators: this represents the number of rows in an HTML table.
            #
            rowString = ngettext("Table with %d row",
                                 "Table with %d rows",
                                  nRows) % nRows
            # Translators: this represents the number of cols in an HTML table.
            #
            colString = ngettext("%d column",
                                 "%d columns",
                                  nColumns) % nColumns
            speech.speak(nonUniformString + " " + rowString + " " + colString)

            obj = table.getAccessibleAt(0, 0)
            self.moveToCell(obj)

        else:
            # Translators: this is for navigating HTML content by
            # moving from table to table.
            #
            speech.speak(_("No more tables."))

    def goNextTable(self, inputEvent):
        """Go to the next table."""
        wrap = True
        [obj, wrapped] = self.findNextRole([pyatspi.ROLE_TABLE], wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            table = obj.queryTable()
            caption = self.getTableCaption(obj)
            if self.queryNonEmptyText(caption):
                text = self.getDisplayedText(caption)
                speech.speak(text)
            nonUniformString = ""
            nonUniform = self.isNonUniformTable(obj)
            if nonUniform:
                # Translators: a uniform table is one in which each table
                # cell occupies one row and one column (i.e. a perfect grid)
                # In contrast, a non-uniform table is one in which at least
                # one table cell occupies more than one row and/or column.
                #
                nonUniformString = _("Non-uniform")
            nRows = table.nRows
            nColumns = table.nColumns
            # Translators: this represents the number of rows in an HTML table.
            #
            rowString = ngettext("Table with %d row",
                                 "Table with %d rows",
                                  nRows) % nRows
            # Translators: this represents the number of cols in an HTML table.
            #
            colString = ngettext("%d column",
                                 "%d columns",
                                  nColumns) % nColumns
            speech.speak(nonUniformString + " " + rowString + " " + colString)
            obj = table.getAccessibleAt(0, 0)
            self.moveToCell(obj)

        else:
            # Translators: this is for navigating HTML content by
            # moving from table to table.
            #
            speech.speak(_("No more tables."))

    def goCellLeft(self, inputEvent):
        """Move to the cell on the left in an HTML table."""
        [obj, characterOffset] = self.getCaretContext()
        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE_CELL],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])
        if obj:
            [row, col] = self.getCellCoordinates(obj)
            oldHeaders = self.getColumnHeaders(obj)
            table = obj.parent.queryTable()
            if self.isSameCell(obj.parent,
                               [row, col],
                               self.lastTableCell):
                # The stored row helps us maintain the correct position
                # when traversing cells that span multiple rows.
                #
                row = self.lastTableCell[0]
            found = False
            while not found and col > 0:
                obj = table.getAccessibleAt(row, col - 1)
                self.lastTableCell = [row, col - 1]
                if not self.isBlankCell(obj) or \
                   not skipBlankCells:
                    found = True
                else:
                    col -= 1

            if found:
                # We only want to speak the header information that has
                # changed, and we don't want to speak headers if we're in
                # a header column.
                #
                if speakCellHeaders and not self.isInHeaderColumn(obj):
                    colHeaders = self.getColumnHeaders(obj)
                    for header in colHeaders:
                        if not header in oldHeaders:
                            text = self.getDisplayedText(header)
                            speech.speak(text)
                self.moveToCell(obj)
            else:
                # Translators: this is for navigating HTML content by
                # moving from table cell to table cell.
                #
                speech.speak(_("Beginning of row."))
        else:
            # Translators: this is for navigating HTML content by
            # moving from table cell to table cell.
            #
            speech.speak(_("Not in a table."))

    def goCellRight(self, inputEvent):
        """Move to the cell on the right in an HTML table."""
        [obj, characterOffset] = self.getCaretContext()
        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE_CELL],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])
        if obj:
            [row, col] = self.getCellCoordinates(obj)
            oldHeaders = self.getColumnHeaders(obj)
            table = obj.parent.queryTable()
            if self.isSameCell(obj.parent,
                               [row, col],
                               self.lastTableCell):
                # The stored row helps us maintain the correct position
                # when traversing cells that span multiple rows.
                #
                row = self.lastTableCell[0]
            colspan = table.getColumnExtentAt(row, col)
            nextCol = col + colspan
            found = False
            while not found and (nextCol <= table.nColumns - 1):
                obj = table.getAccessibleAt(row, nextCol)
                self.lastTableCell = [row, nextCol]
                if not self.isBlankCell(obj) or \
                   not skipBlankCells:
                    found = True
                else:
                    col += 1
                    colspan = table.getColumnExtentAt(row, col)
                    nextCol = col + colspan

            if found:
                # We only want to speak the header information that has
                # changed, and we don't want to speak headers if we're in
                # a header column.
                #
                if speakCellHeaders and not self.isInHeaderColumn(obj):
                    colHeaders = self.getColumnHeaders(obj)
                    for header in colHeaders:
                        if not header in oldHeaders:
                            text = self.getDisplayedText(header)
                            speech.speak(text)
                self.moveToCell(obj)
            else:
                # Translators: this is for navigating HTML content by
                # moving from table cell to table cell.
                #
                speech.speak(_("End of row."))
        else:
            # Translators: this is for navigating HTML content by
            # moving from table cell to table cell.
            #
            speech.speak(_("Not in a table."))

    def goCellUp(self, inputEvent):
        """Move one cell up in an HTML table."""
        [obj, characterOffset] = self.getCaretContext()
        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE_CELL],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])
        if obj:
            [row, col] = self.getCellCoordinates(obj)
            oldHeaders = self.getRowHeaders(obj)
            table = obj.parent.queryTable()
            if self.isSameCell(obj.parent,
                               [row, col],
                               self.lastTableCell):
                # The stored column helps us maintain the correct position
                # when traversing cells that span multiple columns.
                #
                col = self.lastTableCell[1]
            found = False
            while not found and row > 0:
                obj = table.getAccessibleAt(row - 1, col)
                self.lastTableCell = [row - 1, col]
                if not self.isBlankCell(obj) or \
                   not skipBlankCells:
                    found = True
                else:
                    row -= 1

            if found:
                # We only want to speak the header information that has
                # changed, and we don't want to speak headers if we're in
                # a header row.
                #
                if speakCellHeaders and not self.isInHeaderRow(obj):
                    rowHeaders = self.getRowHeaders(obj)
                    for header in rowHeaders:
                        if not header in oldHeaders:
                            text = self.getDisplayedText(header)
                            speech.speak(text)
                self.moveToCell(obj)
            else:
                # Translators: this is for navigating HTML content by
                # moving from table cell to table cell.
                #
                speech.speak(_("Top of column."))
        else:
            # Translators: this is for navigating HTML content by
            # moving from table cell to table cell.
            #
            speech.speak(_("Not in a table."))

    def goCellDown(self, inputEvent):
        """Move one cell down in an HTML table."""
        [obj, characterOffset] = self.getCaretContext()
        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE_CELL],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])
        if obj:
            [row, col] = self.getCellCoordinates(obj)
            oldHeaders = self.getRowHeaders(obj)
            table = obj.parent.queryTable()
            if self.isSameCell(obj.parent,
                               [row, col],
                               self.lastTableCell):
                # The stored column helps us maintain the correct position
                # when traversing cells that span multiple columns.
                #
                col = self.lastTableCell[1]
            rowspan = table.getRowExtentAt(row, col)
            nextRow = row + rowspan
            found = False
            while not found and (nextRow <= table.nRows - 1):
                obj = table.getAccessibleAt(nextRow, col)
                self.lastTableCell = [nextRow, col]
                if not self.isBlankCell(obj) or \
                   not skipBlankCells:
                    found = True
                else:
                    row += 1
                    rowspan = table.getRowExtentAt(row, col)
                    nextRow = row + rowspan

            if found:
                # We only want to speak the header information that has
                # changed, and we don't want to speak headers if we're in
                # a header row.
                #
                if speakCellHeaders and not self.isInHeaderRow(obj):
                    rowHeaders = self.getRowHeaders(obj)
                    for header in rowHeaders:
                        if not header in oldHeaders:
                            text = self.getDisplayedText(header)
                            speech.speak(text)
                self.moveToCell(obj)
            else:
                # Translators: this is for navigating HTML content by
                # moving from table cell to table cell.
                #
                speech.speak(_("Bottom of column."))
        else:
            # Translators: this is for navigating HTML content by
            # moving from table cell to table cell.
            #
            speech.speak(_("Not in a table."))

    def goCellFirst(self, inputEvent):
        """Move to the first cell in an HTML table."""
        [obj, characterOffset] = self.getCaretContext()
        if obj.getRole() != pyatspi.ROLE_TABLE:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])
        if obj:
            obj = obj.queryTable().getAccessibleAt(0, 0)
            self.lastTableCell = [0, 0]
            self.moveToCell(obj)
        else:
            # Translators: this is for navigating HTML content by
            # moving from table cell to table cell.
            #
            speech.speak(_("Not in a table."))

    def goCellLast(self, inputEvent):
        """Move to the last cell in an HTML table."""
        [obj, characterOffset] = self.getCaretContext()
        if obj.getRole() != pyatspi.ROLE_TABLE:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])
        if obj:
            table = obj.queryTable()
            lastRow = table.nRows - 1
            lastCol = table.nColumns - 1
            obj = table.getAccessibleAt(lastRow, lastCol)
            self.lastTableCell = [lastRow, lastCol]
            self.moveToCell(obj)
        else:
            # Translators: this is for navigating HTML content by
            # moving from table cell to table cell.
            #
            speech.speak(_("Not in a table."))

    def goNextLiveRegion(self, inputEvent):
        # First, get any live regions that have been registered as LIVE_NONE
        # because there is no markup to test for these but we still want to 
        # find them
        regobjs = self.liveMngr.getLiveNoneObjects()
        # define our search predicate
        pred = lambda obj: (self.liveMngr.matchLiveRegion(obj) \
                                            or obj in regobjs)
        # start looking
        wrap = True
        [obj, wrapped] = \
                  self.findNextByPredicate(pred, wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            # TODO:   We don't want to move to a list item.  
            # Is this the best place to handle this?
            if obj.getRole() == pyatspi.ROLE_LIST:
                characterOffset = 0
                obj = obj[0]
            else:
                [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            # For debugging
            self.outlineAccessible(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML in a structural
            # manner, where a 'live region' is a location in a web page
            # that are updated without having to refresh the entire page.
            #
            speech.speak(_("No more live regions."))

    def goPreviousLiveRegion(self, inputEvent):
        # First, get any live regions that have been registered as LIVE_NONE
        # because there is no markup to test for these but we still want to 
        # find them
        regobjs = self.liveMngr.getLiveNoneObjects()
        # define our search predicate
        pred = lambda obj: (self.liveMngr.matchLiveRegion(obj) \
                                            or obj in regobjs)
        # start looking
        wrap = True
        [obj, wrapped] = \
                  self.findPrevByPredicate(pred, wrap)
        if wrapped:
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
        if obj:
            # TODO:   We don't want to move to a list item.  
            # Is this the best place to handle this?
            if obj.getRole() == pyatspi.ROLE_LIST:
                characterOffset = 0
            else:
                [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.outlineAccessible(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            # Translators: this is for navigating HTML in a structural
            # manner, where a 'live region' is a location in a web page
            # that are updated without having to refresh the entire page.
            #
            speech.speak(_("No more live regions."))
            
    def goLastLiveRegion(self, inputEvent):
        if settings.inferLiveRegions:
            self.liveMngr.goLastLiveRegion()
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            speech.speak(_("Live region support is off"))

    def advanceLivePoliteness(self, inputEvent):
        """Advances live region politeness level."""
        if settings.inferLiveRegions:
            self.liveMngr.advancePoliteness(orca_state.locusOfFocus)
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            speech.speak(_("Live region support is off"))
            
    def monitorLiveRegions(self, inputEvent):
        if not settings.inferLiveRegions:
            settings.inferLiveRegions = True
            # Translators: this announces to the user that live region
            # are being monitored.
            #
            speech.speak(_("Live regions monitoring on"))
        else:
            settings.inferLiveRegions = False
            # Translators: this announces to the user that live region
            # are not being monitored.
            #
            self.liveMngr.flushMessages()
            speech.speak(_("Live regions monitoring off"))
            
    def setLivePolitenessOff(self, inputEvent):
        if settings.inferLiveRegions:
            self.liveMngr.setLivePolitenessOff()
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            speech.speak(_("Live region support is off"))

    def reviewLiveAnnouncement(self, inputEvent):
        if settings.inferLiveRegions:
            self.liveMngr.reviewLiveAnnouncement( \
                                    int(inputEvent.event_string[1:]))
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            speech.speak(_("Live region support is off"))

    def toggleCaretNavigation(self, inputEvent):
        """Toggles between Firefox native and Orca caret navigation."""

        global controlCaretNavigation

        if controlCaretNavigation:
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.removeByHandler(keyBinding.handler)
            controlCaretNavigation = False
            # Translators: Gecko native caret navigation is where
            # Firefox itself controls how the arrow keys move the caret
            # around HTML content.  It's often broken, so Orca needs
            # to provide its own support.  As such, Orca offers the user
            # the ability to switch between the Firefox mode and the
            # Orca mode.
            #
            string = _("Gecko is controlling the caret.")
        else:
            controlCaretNavigation = True
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.add(keyBinding)
            # Translators: Gecko native caret navigation is where
            # Firefox itself controls how the arrow keys move the caret
            # around HTML content.  It's often broken, so Orca needs
            # to provide its own support.  As such, Orca offers the user
            # the ability to switch between the Firefox mode and the
            # Orca mode.
            #
            string = _("Orca is controlling the caret.")

        debug.println(debug.LEVEL_CONFIGURATION, string)
        speech.speak(string)
        braille.displayMessage(string)

    def toggleStructuralNavigation(self, inputEvent):
        """Toggles structural navigation keys."""

        global structuralNavigationEnabled

        structuralNavigationEnabled = not structuralNavigationEnabled

        if structuralNavigationEnabled:
            # Translators: the structural navigation keys are designed
            # to move the caret around the HTML content by object type.
            # Thus H moves you to the next heading, Shift H to the
            # previous heading, T to the next table, and so on. Some
            # users prefer to turn this off to use Firefox's search
            # when typing feature.  This message is sent to both the
            # braille display and the speech synthesizer when the user
            # toggles the structural navigation feature of Orca.
            # It should be a brief informative message.
            #
            string = _("Structural navigation keys on.")
        else:
            # Translators: the structural navigation keys are designed
            # to move the caret around the HTML content by object type.
            # Thus H moves you to the next heading, Shift H to the
            # previous heading, T to the next table, and so on. Some
            # users prefer to turn this off to use Firefox's search
            # when typing feature.  This message is sent to both the
            # braille display and the speech synthesizer when the user
            # toggles the structural navigation feature of Orca.
            # It should be a brief informative message.
            #
            string = _("Structural navigation keys off.")

        debug.println(debug.LEVEL_CONFIGURATION, string)
        speech.speak(string)
        braille.displayMessage(string)
        
    ####################################################################
    #                                                                  #
    # Match Predicates                                                 #
    #                                                                  #
    ####################################################################

    def __matchChunk(self, obj):
        if obj.getRole() in OBJECT_ROLES:
            text = self.queryNonEmptyText(obj)
            if text and text.characterCount > largeObjectTextLength \
               and not self.isUselessObject(obj):
                return True
            else:
                return False
        else:
            return False

    def __matchLandmark(self, obj):
        if obj is None:
            return False
        attrs = self._getAttrDictionary(obj)
        try:
            if attrs['xml-roles'] in ARIA_LANDMARKS:
                return True
            else:
                return False
        except KeyError:
            return False
