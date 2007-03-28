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

import atspi
import braille
import braillegenerator
import debug
import default
import input_event
import keybindings
import mag
import orca
import orca_state
import rolenames
import settings
import speech
import speechgenerator

from orca_i18n import _
from orca_i18n import ngettext  # for ngettext support

# If True, it tells us to take over caret navigation.  This is something
# that can be set in user-settings.py:
#
# import orca.Gecko
# orca.Gecko.controlCaretNavigation = True
#
controlCaretNavigation = False

# If True, it tells us to position the caret at the beginning of a
# line when arrowing up and down.  If False, we'll try to position the
# caret directly above or below the current caret position.
#
arrowToLineBeginning = True

# Roles that imply their text starts on a new line.
#
NEWLINE_ROLES = [rolenames.ROLE_PARAGRAPH,
                 rolenames.ROLE_SEPARATOR,
                 rolenames.ROLE_LIST_ITEM,
                 rolenames.ROLE_HEADING]

# Roles that represent a logical chunk of information in a document
#
OBJECT_ROLES = [rolenames.ROLE_CHECK_BOX,
                rolenames.ROLE_COLUMN_HEADER,
                rolenames.ROLE_COMBO_BOX,
                rolenames.ROLE_DIAL,
                rolenames.ROLE_ENTRY,
                rolenames.ROLE_HEADING,
                rolenames.ROLE_ICON,
                rolenames.ROLE_LABEL,
                rolenames.ROLE_MENU,
                rolenames.ROLE_MENU_ITEM,
                rolenames.ROLE_PAGE_TAB,
                rolenames.ROLE_PARAGRAPH,
                rolenames.ROLE_PASSWORD_TEXT,
                rolenames.ROLE_PROGRESS_BAR,
                rolenames.ROLE_PUSH_BUTTON,
                rolenames.ROLE_RADIO_BUTTON,
                rolenames.ROLE_RADIO_MENU_ITEM,
                rolenames.ROLE_RADIO_MENU,
                rolenames.ROLE_ROW_HEADER,
                rolenames.ROLE_SLIDER,
                rolenames.ROLE_SPIN_BUTTON,
                rolenames.ROLE_STATUSBAR,
                rolenames.ROLE_TABLE_COLUMN_HEADER,
                rolenames.ROLE_TABLE_ROW_HEADER,
                rolenames.ROLE_TEAR_OFF_MENU_ITEM,
                rolenames.ROLE_TERMINAL,
                rolenames.ROLE_TEXT,
                rolenames.ROLE_TOGGLE_BUTTON,
                rolenames.ROLE_AUTOCOMPLETE]

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
        self.brailleGenerators[rolenames.ROLE_AUTOCOMPLETE] = \
             self._getBrailleRegionsForAutocomplete
        self.brailleGenerators[rolenames.ROLE_ENTRY]        = \
             self._getBrailleRegionsForText
        self.brailleGenerators[rolenames.ROLE_LINK]         = \
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

        self._debugGenerator("_getBrailleRegionsForCheckBox", obj)

        # In document content (I'm not sure about XUL widgets yet), a
        # checkbox is its own little beast with no text.  So...  if it
        # is in document content and has a label, we're likely to be
        # displaying that label already.  If it doesn't have a label,
        # though, we'll display its name.
        #
        text = ""
        if not self._script.inDocumentContent():
            text = self._script.appendString(text, self._script.getDisplayedLabel(obj))
            text = self._script.appendString(text, self._script.getDisplayedText(obj))
        else:
            isLabelled = False
            relations = obj.relations
            if relations:
                for relation in relations:
                    if relation.getRelationType() \
                        == atspi.Accessibility.RELATION_LABELLED_BY:
                        isLabelled = True
                        break
            if not isLabelled and obj.name and len(obj.name):
                text = self._script.appendString(text, obj.name)

        if obj.state.count(atspi.Accessibility.STATE_CHECKED):
            text = self._script.appendString(text, "<x>")
        else:
            text = self._script.appendString(text, "< >")

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

        parent = obj.parent
        if parent.role != rolenames.ROLE_AUTOCOMPLETE:
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

        textRegion = braille.Text(obj, label)
        regions.append(textRegion)
        eol = braille.Region(" $l")
        regions.append(eol)
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

        regions = []

        # With Gecko, a combo box has a menu as a child.  We will use
        # the menu's selection as the text being displayed by the
        # combo box.  In addition, if the LABELLED_BY property is
        # set, we will use it as the label of the combo box.  Otherwise,
        # we'll fall back to the accessible name.
        #
        label = self._script.getDisplayedLabel(obj)
        if not label:
            label = obj.name

        focusedRegionIndex = 0
        if label and len(label):
            regions.append(braille.Region(label + " "))
            focusedRegionIndex = 1

        menu = None
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child.role == rolenames.ROLE_MENU:
                menu = child
                break

        # If the menu is not popped up, then it has no selection and
        # its name is the item that the combo box is showing.  NOTE:
        # This seems to have changed.  See Mozilla bug #363955 and
        # comments below.
        #
        if menu:
            selection = menu.selection
            if selection:
                # The menu might have a selection, but when we go to get
                # the selected item, we get None. In those cases, we'll
                # revert to the name of the menu because that tends to be
                # what text is being presented by the combobox in these cases.
                #
                try:
                    item = selection.getSelectedChild(0)
                    regions.append(braille.Region(item.name))
                except:
                    regions.append(braille.Region(menu.name))
            elif menu.name:
                regions.append(braille.Region(menu.name))

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

    def _getBrailleRegionsForImage(self, obj):
        """Get the braille regions for an image.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForImage", obj)

        regions = []

        text = ""
        text = self._script.appendString(text, self._script.getDisplayedLabel(obj))
        text = self._script.appendString(text, self._script.getDisplayedText(obj))

        # If there's no text for the link, expose part of the
        # link to the user if the image is in a link.
        #
        link = self._script.getContainingLink(obj)
        if len(text) == 0:
            if link:
                [linkRegions, focusedRegion] = \
                    self._getBrailleRegionsForLink(link)
                for region in linkRegions:
                    text += region.string
        elif link:
            text = self._script.appendString(text, self._getTextForRole(link))

        text = self._script.appendString(text, self._getTextForValue(obj))
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

        regions = []

        text = ""
        text = self._script.appendString(text, self._script.getDisplayedLabel(obj))
        text = self._script.appendString(text, self._script.getDisplayedText(obj))

        # If there's no text for the link, expose part of the
        # URI to the user.
        #
        if len(text) == 0:
            basename = self._script.getLinkBasename(obj)
            if basename:
                text = basename

        text = self._script.appendString(text, self._getTextForValue(obj))
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
        self.speechGenerators[rolenames.ROLE_DOCUMENT_FRAME] = \
             self._getSpeechForDocumentFrame
        self.speechGenerators[rolenames.ROLE_ENTRY]          = \
             self._getSpeechForText
        self.speechGenerators[rolenames.ROLE_LINK]           = \
             self._getSpeechForLink

    def _getSpeechForObjectRole(self, obj):
        """Prevents some roles from being spoken."""
        if obj.role in [rolenames.ROLE_PARAGRAPH,
                        rolenames.ROLE_SECTION,
                        rolenames.ROLE_LABEL,
                        rolenames.ROLE_LIST_ITEM,
                        rolenames.ROLE_UNKNOWN]:
            return []
        else:
            return [rolenames.getSpeechForRoleName(obj)]

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
        utterances.extend(self._getSpeechForObjectRole(obj))

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

        parent = obj.parent
        if parent.role != rolenames.ROLE_AUTOCOMPLETE:
            return speechgenerator.SpeechGenerator._getSpeechForText(
                self, obj, already_focused)

        utterances = []

        # This is the main difference between this class and the default
        # class - we'll give this thing a name here, and we'll make it
        # be the name of the autocomplete.
        #
        label = self._script.getDisplayedLabel(parent)
        if not label or not len(label):
            label = parent.name
        utterances.append(label)

        utterances.extend(self._getSpeechForObjectRole(obj))

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

        utterances = []

        # With Gecko, a combo box has a menu as a child.  We will use
        # the menu's selection as the text being displayed by the
        # combo box.  In addition, if the LABELLED_BY property is
        # set, we will use it as the label of the combo box.  Otherwise,
        # we'll fall back to the accessible name.
        #
        label = self._script.getDisplayedLabel(obj)
        if not label:
            label = obj.name

        if not already_focused and label:
            utterances.append(label)

        if not already_focused:
            utterances.extend(self._getSpeechForObjectRole(obj))

        menu = None
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child.role == rolenames.ROLE_MENU:
                menu = child
                break

        # If the menu is not popped up, then it has no selection and
        # its name is the item that the combo box is showing.  NOTE:
        # This seems to have changed.  See Mozilla bug #363955 and
        # comments below.
        #
        if menu:
            selection = menu.selection
            if selection:
                # The menu might have a selection, but when we go to get
                # the selected item, we get None. In those cases, we'll
                # revert to the name of the menu because that tends to be
                # what text is being presented by the combobox in these cases.
                #
                try:
                    item = selection.getSelectedChild(0)
                    utterances.append(item.name)
                except:
                    utterances.append(menu.name)
            elif menu.name:
                utterances.append(menu.name)

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForComboBox",
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
            link = self._script.getContainingLink(obj)
            if not len(utterances):
                if link:
                    utterances.extend(self._getSpeechForLink(link,
                                                             already_focused))
            elif link:
                utterances.extend(self._getSpeechForObjectRole(link))

            utterances.extend(self._getSpeechForObjectRole(obj))

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

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)

            # If there's no text for the link, expose part of the
            # URI to the user.
            #
            if not len(utterances):
                basename = self._script.getLinkBasename(obj)
                if basename:
                    utterances.append(basename)

            utterances.extend(self._getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForLink",
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

        if not obj:
            return utterances

        if obj is stopAncestor:
            return utterances

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break

            # We try to omit things like fillers off the bat...
            #
            if (parent.role == rolenames.ROLE_FILLER) \
                or (parent.role == rolenames.ROLE_FORM) \
                or (parent.role == rolenames.ROLE_LINK) \
                or (parent.role == rolenames.ROLE_LIST_ITEM) \
                or (parent.role == rolenames.ROLE_LIST) \
                or (parent.role == rolenames.ROLE_PARAGRAPH) \
                or (parent.role == rolenames.ROLE_SECTION) \
                or (parent.role == rolenames.ROLE_LAYERED_PANE) \
                or (parent.role == rolenames.ROLE_SPLIT_PANE) \
                or (parent.role == rolenames.ROLE_SCROLL_PANE) \
                or (parent.role == rolenames.ROLE_UNKNOWN) \
                or (self._script.isLayoutOnly(parent)):
                parent = parent.parent
                continue

            # Skip unfocusable menus.  This is for earlier versions
            # of Firefox where menus were nested in kind of an odd
            # dual nested menu hierarchy.
            #
            if (parent.role == rolenames.ROLE_MENU) \
               and not parent.state.count(atspi.Accessibility.STATE_FOCUSABLE):
                parent = parent.parent
                continue

            # Well...if we made it this far, we will now append the
            # role, then the text, and then the label.
            #
            if parent.role != rolenames.ROLE_TABLE_CELL:
                utterances.append(rolenames.getSpeechForRoleName(parent))

            # Now...autocompletes are wierd.  We'll let the handling of
            # the entry give us the name.
            #
            if parent.role == rolenames.ROLE_AUTOCOMPLETE:
                parent = parent.parent
                continue

            # Well...now we skip the parent if it's accessible text is
            # a single EMBEDDED_OBJECT_CHARACTER.  The reason for this
            # is that it Script.getDisplayedText will end up coming
            # back to the children of an object for the text in the
            # children if an object's text contains an
            # EMBEDDED_OBJECT_CHARACTER.
            #
            if parent.text:
                displayedText = parent.text.getText(0, -1)
                unicodeText = displayedText.decode("UTF-8")
                if unicodeText \
                    and (len(unicodeText) == 1) \
                    and (unicodeText[0] == self._script.EMBEDDED_OBJECT_CHARACTER):
                    parent = parent.parent
                    continue

            # Finally, put in the text and label (if they exist)
            #
            text = self._script.getDisplayedText(parent)
            label = self._script.getDisplayedLabel(parent)
            if text and (text != label) and len(text):
                utterances.append(text)
            if label and len(label):
                utterances.append(label)

            parent = parent.parent

        utterances.reverse()

        return utterances

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

        # _caretNavigationFunctions are functions that represent fundamental
        # ways to move the caret (e.g., by the arrow keys).
        #
        self._caretNavigationFunctions = \
            [Script.goNextCharacter,
             Script.goPreviousCharacter,
             Script.goNextWord,
             Script.goPreviousWord,
             Script.goNextLine,
             Script.goPreviousLine]

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
             Script.goNextList,
             Script.goPreviousList,
             Script.goNextListItem,
             Script.goPreviousListItem,
             Script.goNextUnvisitedLink,
             Script.goPreviousUnvisitedLink,
             Script.goNextVisitedLink,
             Script.goPreviousVisitedLink,
             Script.goNextTable,
             Script.goPreviousTable,
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
                "Goes to next character.")

        self.inputEventHandlers["goPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousCharacter,
                "Goes to previous character.")

        self.inputEventHandlers["goNextWordHandler"] = \
            input_event.InputEventHandler(
                Script.goNextWord,
                "Goes to next word.")

        self.inputEventHandlers["goPreviousWordHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousWord,
                "Goes to previous word.")

        self.inputEventHandlers["goNextLineHandler"] = \
            input_event.InputEventHandler(
                Script.goNextLine,
                "Goes to next line.")

        self.inputEventHandlers["goPreviousLineHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousLine,
                "Goes to previous line.")

        self.inputEventHandlers["goCellLeftHandler"] = \
            input_event.InputEventHandler(
                Script.goCellLeft,
                "Goes left one cell.")

        self.inputEventHandlers["goCellRightHandler"] = \
            input_event.InputEventHandler(
                Script.goCellRight,
                "Goes right one cell.")

        self.inputEventHandlers["goCellDownHandler"] = \
            input_event.InputEventHandler(
                Script.goCellDown,
                "Goes down one cell.")

        self.inputEventHandlers["goCellUpHandler"] = \
            input_event.InputEventHandler(
                Script.goCellUp,
                "Goes up one cell.")

        self.inputEventHandlers["goCellFirstHandler"] = \
            input_event.InputEventHandler(
                Script.goCellFirst,
                "Goes to the first cell in a table.")

        self.inputEventHandlers["goCellLastHandler"] = \
            input_event.InputEventHandler(
                Script.goCellLast,
                "Goes to the last cell in a table.")

        self.inputEventHandlers["goPreviousHeadingHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading,
                "Goes to previous heading.")

        self.inputEventHandlers["goNextHeadingHandler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading,
                "Goes to next heading.")

        self.inputEventHandlers["goPreviousHeading1Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading1,
                "Goes to previous heading at level 1.")

        self.inputEventHandlers["goNextHeading1Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading1,
                "Goes to next heading at level 1.")

        self.inputEventHandlers["goPreviousHeading2Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading2,
                "Goes to previous heading at level 2.")

        self.inputEventHandlers["goNextHeading2Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading2,
                "Goes to next heading at level 2.")

        self.inputEventHandlers["goPreviousHeading3Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading3,
                "Goes to previous heading at level 3.")

        self.inputEventHandlers["goNextHeading3Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading3,
                "Goes to next heading at level 3.")

        self.inputEventHandlers["goPreviousHeading4Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading4,
                "Goes to previous heading at level 4.")

        self.inputEventHandlers["goNextHeading4Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading4,
                "Goes to next heading at level 4.")

        self.inputEventHandlers["goPreviousHeading5Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading5,
                "Goes to previous heading at level 5.")

        self.inputEventHandlers["goNextHeading5Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading5,
                "Goes to next heading at level 5.")

        self.inputEventHandlers["goPreviousHeading6Handler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading6,
                "Goes to previous heading at level 6.")

        self.inputEventHandlers["goNextHeading6Handler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading6,
                "Goes to next heading at level 6.")

        self.inputEventHandlers["goPreviousChunkHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousChunk,
                "Goes to previous large object.")

        self.inputEventHandlers["goNextChunkHandler"] = \
            input_event.InputEventHandler(
                Script.goNextChunk,
                "Goes to next large object.")

        self.inputEventHandlers["goPreviousListHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousList,
                "Goes to previous list.")

        self.inputEventHandlers["goNextListHandler"] = \
            input_event.InputEventHandler(
                Script.goNextList,
                "Goes to next list.")

        self.inputEventHandlers["goPreviousListItemHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousListItem,
                "Goes to previous list item.")

        self.inputEventHandlers["goNextListItemHandler"] = \
            input_event.InputEventHandler(
                Script.goNextListItem,
                "Goes to next list item.")

        self.inputEventHandlers["goPreviousUnvisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousUnvisitedLink,
                "Goes to previous unvisited link.")

        self.inputEventHandlers["goNextUnvisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goNextUnvisitedLink,
                "Goes to next unvisited link.")

        self.inputEventHandlers["goPreviousVisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousVisitedLink,
                "Goes to previous visited link.")

        self.inputEventHandlers["goNextVisitedLinkHandler"] = \
            input_event.InputEventHandler(
                Script.goNextVisitedLink,
                "Goes to next visited link.")

        self.inputEventHandlers["goPreviousTableHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousTable,
                "Goes to previous table.")

        self.inputEventHandlers["goNextTableHandler"] = \
            input_event.InputEventHandler(
                Script.goNextTable,
                "Goes to next table.")

        self.inputEventHandlers["toggleCaretNavigationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleCaretNavigation,
                "Switches between Firefox native and Orca caret navigation.")

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

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                0,
                self.inputEventHandlers["goNextCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                0,
                self.inputEventHandlers["goPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                self.inputEventHandlers["goNextWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                self.inputEventHandlers["goPreviousWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Up",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                0,
                self.inputEventHandlers["goPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                0,
                self.inputEventHandlers["goNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                self.inputEventHandlers["goCellRightHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                self.inputEventHandlers["goCellLeftHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Up",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                self.inputEventHandlers["goCellUpHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                self.inputEventHandlers["goCellDownHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Home",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                self.inputEventHandlers["goCellFirstHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "End",
                (1 << atspi.Accessibility.MODIFIER_CONTROL \
                 | 1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                self.inputEventHandlers["goCellLastHandler"]))

        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        # NOTE: We include ALT and CONTROL in all the bindings below so as
        # to not conflict with menu and other mnemonics.

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "1",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeading1Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "1",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextHeading1Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "2",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeading2Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "2",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextHeading2Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "3",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeading3Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "3",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextHeading3Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "4",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeading4Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "4",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextHeading4Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "5",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextHeading5Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "5",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeading5Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "6",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeading6Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "6",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextHeading6Handler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousChunkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextChunkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousListHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextListHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousListItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextListItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousUnvisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextUnvisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "v",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousVisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "v",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextVisitedLinkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "t",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousTableHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "t",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT \
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                0,
                self.inputEventHandlers["goNextTableHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "F12",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["toggleCaretNavigationHandler"]))

        if controlCaretNavigation:
            for keyBinding in self.__getArrowBindings().keyBindings:
                keyBindings.add(keyBinding)

        return keyBindings

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
            if handler and handler._function in self._caretNavigationFunctions:
                return self.useCaretNavigationModel(keyboardEvent)
            elif handler \
                and handler._function in self._structuralNavigationFunctions:
                return self.useStructuralNavigationModel()
            else:
                consumes = handler != None
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler and handler._function in self._caretNavigationFunctions:
                return self.useCaretNavigationModel(keyboardEvent)
            elif handler \
                and handler._function in self._structuralNavigationFunctions:
                return self.useStructuralNavigationModel()
            else:
                consumes = handler != None
        return consumes

    def onCaretMoved(self, event):
        """Caret movement in Gecko is somewhat unreliable and
        unpredictable, but we need to handle it.  When we detect caret
        movement, we make sure we update our own notion of the caret
        position: our caretContext is an [obj, characterOffset] that
        points to our current item and character (if applicable) of
        interest.  If our current item doesn't implement the
        accessible text specialization, the characterOffset value
        is meaningless (and typically -1)."""

        # We'll just always assume that the thing in which the caret
        # moved is the locus of focus.
        #
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

        #print "HERE: caretContext=", self.caretContext
        #print "            source=", event.source
        #print "       caretOffset=", event.source.text.caretOffset
        #print "    characterCount=", event.source.text.characterCount


        self.caretContext = self.findFirstCaretContext(\
            event.source,
            event.source.text.caretOffset)
        [obj, characterOffset] = self.caretContext

        # Save where we are in this particular document frame.
        # We do this because the user might have several URLs
        # open in several different tabs, and we keep track of
        # where the caret is for each documentFrame.
        #
        documentFrame = self.getDocumentFrame()
        if documentFrame:
            self._documentFrameCaretContext[documentFrame] = self.caretContext

        #print "       ended up at=", self.caretContext

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
            string = orca_state.lastInputEvent.event_string
            mods = orca_state.lastInputEvent.modifiers
            if (string == "Left") or (string == "Right"):
                [obj, characterOffset] = self.caretContext
                self.targetCharacterExtents = \
                    self.getExtents(obj,
                                    characterOffset,
                                    characterOffset + 1)

        default.Script.onCaretMoved(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an an object.

        Arguments:
        - event: the Event
        """
        # If text is deleted from an object, we want to trash our
        # cache of the unicode text.
        #
        try:
            del event.source.unicodeText
        except:
            pass

        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        # If text is inserted into an object, we want to trash our
        # cache of the unicode text.
        #
        try:
            del event.source.unicodeText
        except:
            pass

        default.Script.onTextInserted(self, event)

    def onDocumentReload(self, event):
        """Called when the reload button is hit for a web page."""
        self._loadingDocumentContent = True
        # [[[TODO: WDW - Currently, we handle loading notification by
        # looking at the state changed events on the document frame
        # (we care about busy state there) and visibility/value changes
        # on the progress bar.]]]
        #
        self._loadingDocumentContent = True
        pass

    def onDocumentLoadComplete(self, event):
        """Called when a web page load is completed."""
        # [[[TODO: WDW - Currently, we handle loading notification by
        # looking at the state changed events on the document frame
        # (we care about busy state there) and visibility/value changes
        # on the progress bar.]]]
        #
        self._loadingDocumentContent = False
        pass

    def onDocumentLoadStopped(self, event):
        """Called when a web page load is interrupted."""
        # [[[TODO: WDW - Currently, we handle loading notification by
        # looking at the state changed events on the document frame
        # (we care about busy state there) and visibility/value changes
        # on the progress bar.]]]
        #
        self._loadingDocumentContent = False
        pass

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """
        # We ignore these because Gecko just happily keeps generating
        # name changed events for objects whose name don't change.
        #
        return

    def onFocus(self, event):
        # We're going to ignore focus events on the frame.  They
        # are often intermingled with menu activity, wreaking havoc
        # on the context.
        #
        if (event.source.role == rolenames.ROLE_FRAME) \
           or (not len(event.source.role)):
            return

        # We also ignore focus events on the panel that holds the document
        # frame.  We end up getting these typically because we've called
        # grabFocus on this panel when we're doing caret navigation.  In
        # those cases, we want the locus of focus to be the subcomponent
        # that really holds the caret.
        #
        if event.source.role == rolenames.ROLE_PANEL:
            documentFrame = self.getDocumentFrame()
            if documentFrame and (documentFrame.parent == event.source):
                return

        # When we get a focus event on the document frame, it's usually
        # because we did a grabFocus on its parent in setCaretPosition.
        # We try to handle this here by seeing if there is already a
        # caret context for the document frame.  If we succeed, then
        # we set the focus on the object that's holding the caret.
        #
        if event.source \
            and (event.source.role == rolenames.ROLE_DOCUMENT_FRAME):
            try:
                [obj, characterOffset] = self.caretContext
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
        #if (event.source.role == rolenames.ROLE_MENU) \
        #   and event.source.parent \
        #   and (event.source.parent.role == rolenames.ROLE_MENU_BAR):
        #    return

        # Gecko's combo boxes are a bit of a struggle to work with.
        # First of all, the combo box is a container for a menu.
        # When you arrow up and down in them, the menu item gets
        # focus and then we see name changed events for the menu
        # to represent the name of the menu item that was just
        # selected.  It's all wonderfully convoluted.
        #
        if (event.source.role == rolenames.ROLE_MENU_ITEM):
            parent = event.source.parent
            if parent and (parent.role == rolenames.ROLE_COMBO_BOX):
                orca.setLocusOfFocus(event, parent)
                orca.visualAppearanceChanged(event, parent)
                return
            elif parent and (parent.role == rolenames.ROLE_MENU):
                parent = parent.parent
                if parent and (parent.role == rolenames.ROLE_COMBO_BOX):
                    orca.setLocusOfFocus(event, parent, False)
                    orca.visualAppearanceChanged(event, parent)
                    return

        # Autocomplete widgets are a complex beast as well.  When they
        # get focus, their child (which is an entry) really has focus.
        # Their child also issues a focus: event, so we just ignore
        # the autocomplete focus: event.
        #
        if event.source.role == rolenames.ROLE_AUTOCOMPLETE:
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
        if event.source.role == rolenames.ROLE_LINK:
            containingLink = self.getContainingLink(orca_state.locusOfFocus)
            if containingLink == event.source:
                return
            elif event.source.childCount == 1:
                child = event.source.child(0)
                orca.setLocusOfFocus(event, child)
                return

        default.Script.onFocus(self, event)

    def onLinkSelected(self, event):
        # NOTE: In Firefox 3, link selected events are not issued when
        # a link is selected.  Instead, they've decided to issue focus:
        # events when a link is selected.  This is 'old' code leftover
        # from Yelp and Firefox 2.
        #
        text = event.source.text
        hypertext = event.source.hypertext
        linkIndex = self.getLinkIndex(event.source, text.caretOffset)

        if linkIndex >= 0:
            link = hypertext.getLink(linkIndex)
            linkText = self.getText(event.source,
                                    link.startIndex,
                                    link.endIndex)
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            #print "onLinkSelected", event.source.role, string,
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
            linkText = self.getText(event.source, 0, -1)
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        else:
            speech.speak(_("link"), self.voices[settings.HYPERLINK_VOICE])

        self.updateBraille(event.source)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # We care when the document frame changes it's busy state.  That
        # means it has started/stopped loading content.
        #
        if event.type == "object:state-changed:busy":
            if event.source \
                and (event.source.role == rolenames.ROLE_DOCUMENT_FRAME):
                if event.detail1:
                    self._loadingDocumentContent = True
                    message = _("Loading.  Please wait.")
                    braille.displayMessage(message)
                    speech.stop()
                    speech.speak(message)
                elif event.source.name:
                    self._loadingDocumentContent = False
                    message = _("Finished loading %s.") % event.source.name
                    braille.displayMessage(message)
                    speech.stop()
                    speech.speak(message)
                else:
                    self._loadingDocumentContent = False
                    message = _("Finished loading.")
                    braille.displayMessage(message)
                    speech.stop()
                    speech.speak(message)
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
        if (event.source.role == rolenames.ROLE_FRAME) \
            and event.source.state.count(atspi.Accessibility.STATE_ACTIVE):
            documentFrame = self.getDocumentFrame()
            try:
                self.caretContext = self._documentFrameCaretContext[\
                    documentFrame]
            except:
                self.caretContext = self.findNextCaretInOrder(documentFrame)
                self._documentFrameCaretContext[documentFrame] = \
                    self.caretContext

            #print "HERE", documentFrame.name
            #print "    ", documentFrame
            #print "    ", documentFrame.parent

            braille.displayMessage(documentFrame.name)
            speech.stop()
            speech.speak(
                "%s %s" \
                % (documentFrame.name,
                   rolenames.rolenames[rolenames.ROLE_PAGE_TAB].speech))

            # [[[TODO: WDW - commented this out.  It is an attempt to
            # read the line at the current character offset for the
            # window, but it doesn't seem to be reliable.]]]
            #
            #if self.caretContext:
            #    [obj, characterOffset] = self.caretContext
            #    self.updateBraille(obj)
            #    self.speakContents(
            #        self.getLineContentsAtOffset(obj,
            #                                     characterOffset))

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

        # We'll try to give some presentation of progress level for
        # loading the document content if we can.  [[[TODO: HACK - WDW
        # I've been filling the talkback buffers with Firefox crashes
        # all day today.  Looks like Gecko wants to crash when you
        # probe things about progress bars.  Maybe it's a passive
        # aggressive way of saying "HEY! QUIT CHECKING MY STATUS!
        # I'LL TELL YOU WHEN I'M DONE!!!".  So...we won't offer
        # this feature right now.]]]
        #
        if False and obj.role == rolenames.ROLE_PROGRESS_BAR:
            if self._loadingDocumentContent:
                [regions, focusedRegion] = \
                    self.brailleGenerator.getBrailleRegions(event.source)
                braille.clear()
                line = braille.Line()
                braille.addLine(line)
                braille.setFocus(focusedRegion)
                braille.refresh(True)
                if not speech.isSpeaking():
                    speech.speakUtterances(\
                        self.speechGenerator.getSpeech(event.source, True))
                return

        if (obj.role == rolenames.ROLE_CHECK_BOX) \
            and obj.state.count(atspi.Accessibility.STATE_FOCUSED):
            orca.setLocusOfFocus(event, obj, False)

        default.Script.visualAppearanceChanged(self, event, obj)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # Try to handle the case where a spurious focus event was tossed
        # at us.
        #
        if newLocusOfFocus and self.inDocumentContent(newLocusOfFocus):
            if newLocusOfFocus.text:
                caretOffset = newLocusOfFocus.text.caretOffset
            else:
                caretOffset = 0
            self.caretContext = self.findFirstCaretContext(newLocusOfFocus,
                                                           caretOffset)

        # Don't bother speaking all the information about the HTML
        # container - it's duplicated all over the place.  So, we
        # just speak the role.
        #
        if newLocusOfFocus \
           and newLocusOfFocus.role == rolenames.ROLE_HTML_CONTAINER:
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
        #    and newLocusOfFocus.role == rolenames.ROLE_LINK:
        #    # Gecko issues focus: events for a link when you move the
        #    # caret to or tab to a link.  By the time we've gotten here,
        #    # though, we've already presented the link via a caret moved
        #    # event or some other event.  So...we don't anything.
        #    #
        #    try:
        #        [obj, characterOffset] = self.caretContext
        #        if newLocusOfFocus == obj:
        #            return
        #    except:
        #        pass

        default.Script.locusOfFocusChanged(self,
                                           event,
                                           oldLocusOfFocus,
                                           newLocusOfFocus)

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the give object.

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
        lineContentsOffset = focusedCharacterOffset
        if focusedObj.text:
            char = self.getText(focusedObj,
                                focusedCharacterOffset,
                                focusedCharacterOffset + 1)
            if char == "\n":
                lineContentsOffset = max(0, focusedCharacterOffset - 1)

        contents = self.getLineContentsAtOffset(focusedObj,
                                                max(0, lineContentsOffset))

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

            # [[[TODO: WDW - Something odd is going on with text
            # entries and checkboxes and other things: we are ending
            # up with different accessibles for the same object.  I'm
            # not sure if this is a Firefox bug or an Orca bug, but
            # it's wreaking havoc on us.  This is a hack to try to
            # get around that.]]]
            #
            isFocusedObj = \
                (obj == focusedObj) \
                or ((obj.role == focusedObj.role) \
                    and (obj.name == focusedObj.name) \
                    and (obj.parent == focusedObj.parent)) \
                or obj.state.count(atspi.Accessibility.STATE_FOCUSED)

            # [[[TODO: WDW - one more stab before we say it is the focused
            # object.  If the text attributes are different, we definitely
            # know they are not the same.]]]
            #
            if isFocusedObj:
                if obj.text:
                    if not focusedObj.text:
                        isFocusedObj = False
                    else:
                        string1 = self.getText(obj,
                                               startOffset,
                                               endOffset)
                        string2 = self.getText(focusedObj,
                                               startOffset,
                                               endOffset)
                        isFocusedObj = string1 == string2
                else:
                    isFocusedObj = not focusedObj.text

            if obj.role in [rolenames.ROLE_ENTRY,
                            rolenames.ROLE_PASSWORD_TEXT] \
                or ((obj.role == rolenames.ROLE_DOCUMENT_FRAME) \
                    and obj.state.count(atspi.Accessibility.STATE_EDITABLE)):
                label = self.getDisplayedLabel(obj)
                regions = [braille.Text(obj, label)]
                eol = braille.Region(" $l")
                regions.append(eol)
                if isFocusedObj:
                    focusedRegion = regions[0]
            elif obj.text:
                string = self.getText(obj, startOffset, endOffset)
                regions = [braille.Region(
                    string,
                    focusedCharacterOffset - startOffset)]
                if obj.role == rolenames.ROLE_LINK:
                    link = obj
                else:
                    link = self.getContainingLink(obj)
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

            if len(line.regions):
                line.addRegion(braille.Region(" "))

            line.addRegions(regions)

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
        if obj.text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the previous character.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next character via
            # a call to goNextWord.]]]
            #
            foo = self.getText(obj, 0, -1)
            if characterOffset >= len(foo):
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
        if obj.text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the previous word.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next word via
            # a call to goNextWord.]]]
            #
            foo = self.getText(obj, 0, -1)
            if characterOffset >= len(foo):
                print "YIKES in Gecko.sayWord!"
                characterOffset -= 1

        self.speakContents(self.getWordContentsAtOffset(obj, characterOffset))

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent():
            default.Script.sayLine(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        if obj.text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the current line.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next line via
            # a call to goNextLine.]]]
            #
            foo = self.getText(obj, 0, -1)
            if characterOffset >= len(foo):
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
        if obj.role != rolenames.ROLE_DOCUMENT_FRAME and obj.text:
            string = self.getText(obj, 0, -1)
        else:
            string = ""
        print obj, obj.name, obj.role, \
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
        del self.caretContext
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            if True or obj.state.count(atspi.Accessibility.STATE_SHOWING):
                if obj.text:
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
            if obj and obj.state.count(atspi.Accessibility.STATE_SHOWING):
                characterExtents = self.getExtents(
                    obj, characterOffset, characterOffset + 1)
                if lastObj and (lastObj != obj):
                    if obj.role == rolenames.ROLE_LIST_ITEM:
                        contents += "\n"
                    if lastObj.role == rolenames.ROLE_LINK:
                        contents += ">"
                    elif (lastCharacterExtents[1] < characterExtents[1]):
                        contents += "\n"
                    elif obj.role == rolenames.ROLE_TABLE_CELL:
                        parent = obj.parent
                        if parent.table.getColumnAtIndex(obj.index) != 0:
                            contents += " "
                    elif obj.role == rolenames.ROLE_LINK:
                        contents += "<"
                contents += self.getCharacterAtOffset(obj, characterOffset)
                [lastObj, lastCharacterOffset] = [obj, characterOffset]
                lastCharacterExtents = characterExtents
            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)
        if lastObj and lastObj.role == rolenames.ROLE_LINK:
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
                if obj.text:
                    string += "[%s] text='%s' " % (obj.role,
                                                   self.getText(obj,
                                                                startOffset,
                                                                endOffset))
                else:
                    string += "[%s] name='%s' " % (obj.role, obj.name)
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

    def inDocumentContent(self, obj=None):
        """Returns True if the given object (defaults to the current
        locus of focus is in the document content).
        """
        if not obj:
            obj = orca_state.locusOfFocus
        while obj:
            if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
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
        for i in range(0, self.app.childCount):
            child = self.app.child(i)
            if child.role == rolenames.ROLE_FRAME:
                relations = child.relations
                for relation in relations:
                    if relation.getRelationType()  \
                        == atspi.Accessibility.RELATION_EMBEDS:
                        documentFrame = atspi.Accessible.makeAccessible( \
                            relation.getTarget(0))
                        if documentFrame.state.count( \
                            atspi.Accessibility.STATE_SHOWING):
                            break
                        else:
                            documentFrame = None

        return documentFrame

    def getUnicodeText(self, obj):
        """Returns the unicode text for an object or None if the object
        doesn't implement the accessible text specialization.
        """

        # We cache the text once we get it.
        #
        try:
            return obj.unicodeText
        except:
            if obj.text:
                obj.unicodeText = self.getText(obj, 0, -1).decode("UTF-8")
            else:
                obj.unicodeText = None
        return obj.unicodeText

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if we should do our own caret navigation.
        """

        if not controlCaretNavigation:
            return False

        if not self.inDocumentContent():
            return False

        weHandleIt = True
        obj = orca_state.locusOfFocus
        if obj and (obj.role == rolenames.ROLE_ENTRY):
            text        = obj.text
            length      = text.characterCount
            caretOffset = text.caretOffset
            singleLine  = obj.state.count(
                atspi.Accessibility.STATE_SINGLE_LINE)
            if length == 0:
                weHandleIt = True
            elif caretOffset <= 0:
                weHandleIt = keyboardEvent.event_string \
                             in ["Up", "Left"]
            elif caretOffset >= length - 1:
                weHandleIt = keyboardEvent.event_string \
                             in ["Down", "Right"]
            else:
                weHandleIt = False

            if singleLine and not weHandleIt:
                weHandleIt = keyboardEvent.event_string in ["Up", "Down"]

        elif keyboardEvent.modifiers & (1 << atspi.Accessibility.MODIFIER_ALT):
            # We won't handle keyboard events with Alt in them since
            # they are for things like going back in history and
            # opening and closing combo boxes.
            #
            weHandleIt = False

        elif obj and (obj.role == rolenames.ROLE_COMBO_BOX):
            # We'll let Firefox handle the navigation of combo boxes.
            #
            weHandleIt = keyboardEvent.event_string in ["Left", "Right"]

        elif obj and (obj.role == rolenames.ROLE_MENU_ITEM):
            # We'll let Firefox handle the navigation of combo boxes.
            #
            parent = obj.parent
            if parent:
                parent = parent.parent
                if parent and (parent.role == rolenames.ROLE_COMBO_BOX):
                    weHandleIt = \
                        keyboardEvent.event_string in ["Left", "Right"]

        return weHandleIt

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation.
        [[[TODO: WDW - this should return False if we're in something
        like an entry area or a list because we want their keyboard
        navigation stuff to work.]]]
        """

        letThemDoItRoles = [rolenames.ROLE_ENTRY,
                            rolenames.ROLE_TEXT,
                            rolenames.ROLE_PASSWORD_TEXT]

        obj = orca_state.locusOfFocus
        while obj:
            if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
                # Don't use the structural navivation model if the
                # user is editing the document.
                return not obj.state.count(atspi.Accessibility.STATE_EDITABLE)
            elif obj.role in letThemDoItRoles:
                return not obj.state.count(atspi.Accessibility.STATE_EDITABLE)
            else:
                obj = obj.parent

        return False

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

        # [[[TODO: WDW - HACK to handle the fact that
        # hyperlink.startIndex and hyperlink.endIndex is broken in the
        # Gecko a11y implementation.  This will hopefully be fixed.
        # If it is, one should be able to use hyperlink.startIndex.]]]
        #
        # We also cache the offset so we don't need to do this each time
        # we come to this object.
        #
        try:
            return obj.characterOffsetInParent
        except:
            if obj.hyperlink:
                index = 0
                text = self.getUnicodeText(obj.parent)
                if text:
                    for offset in range(0, len(text)):
                        if text[offset] == self.EMBEDDED_OBJECT_CHARACTER:
                            if index == obj.index:
                                obj.characterOffsetInParent = offset
                                break
                            else:
                                index += 1
                else:
                    obj.characterOffsetInParent = -1
            else:
                obj.characterOffsetInParent = -1

        try:
            return obj.characterOffsetInParent
        except:
            # If this is issued, something is broken in the AT-SPI
            # implementation.
            #
            debug.printException(debug.LEVEL_SEVERE)
            return -1

    def getChildIndex(self, obj, characterOffset):
        """Given an object that implements accessible text, determine
        the index of the child that is represented by an
        EMBEDDED_OBJECT_CHARACTER at characterOffset in the object's
        accessible text."""

        # We cache these offsets so we don't need to keep finding them
        # over and over again.
        #
        try:
            indices = obj.childrenIndices
        except:
            obj.childrenIndices = {}

        try:
            return obj.childrenIndices[characterOffset]
        except:
            obj.childrenIndices[characterOffset] = -1
            unicodeText = self.getUnicodeText(obj)
            if unicodeText \
               and (unicodeText[characterOffset] \
                    == self.EMBEDDED_OBJECT_CHARACTER):
                index = -1
                for character in range(0, characterOffset + 1):
                    if unicodeText[character] \
                        == self.EMBEDDED_OBJECT_CHARACTER:
                        index += 1
                obj.childrenIndices[characterOffset] = index

        return obj.childrenIndices[characterOffset]

    def getExtents(self, obj, startOffset, endOffset):
        """Returns [x, y, width, height] of the text at the given offsets
        if the object implements accessible text, or just the extents of
        the object if it doesn't implement accessible text.
        """
        if not obj:
            return [0, 0, 0, 0]
        if obj.text:
            extents = obj.text.getRangeExtents(startOffset, endOffset, 0)
        else:
            ext = obj.extents
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
        if lowestTop < highestBottom:
            overlapAmount = highestBottom - lowestTop
            shortestHeight = min(a[3], b[3])
            return ((1.0 * overlapAmount) / shortestHeight) > 0.25
        else:
            return False

    def isLabellingContents(self, obj, contents):
        """Given and obj and a list of [obj, startOffset, endOffset] tuples,
        determine if obj is labelling anything in the tuples."""

        if obj.role != rolenames.ROLE_LABEL:
            return False

        relations = obj.relations
        if not relations:
            return False

        for relation in relations:
            if relation.getRelationType() \
                == atspi.Accessibility.RELATION_LABEL_FOR:
                for i in range(0, relation.getNTargets()):
                    target = atspi.Accessible.makeAccessible(\
                        relation.getTarget(i))
                    for content in contents:
                        if content[0] == target:
                            return True

        return False

    def getAutocompleteEntry(self, obj):
        """Returns the ROLE_ENTRY object of a ROLE_AUTOCOMPLETE object or
        None if the entry cannot be found.
        """
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child and (child.role == rolenames.ROLE_ENTRY):
                return child
        return None

    def getCellCoordinates(self, obj):
        """Returns the [row, col] of a ROLE_TABLE_CELL or [0, 0] if this
        if the coordinates cannot be found.
        """

        # [[[TODO: WDW - we do this here because Gecko's table interface
        # is broken and does not give us valid answers.  So...we hack
        # and try to find the coordinates in other ways.  We assume
        # the cells are laid out in row/column order, thus allowing us
        # to do some easy math to find the coordinated.]]]
        #
        parent = obj.parent
        if parent and parent.table:
            # row = obj.index / parent.table.nColumns
            # col = obj.index % parent.table.nColumns
            # return [row, col]
            #
            # By the way, here's the proper way to do it, since we
            # cannot always depend upon the ordering of the children.
            # Easy if it works...
            #
            # NOTE from Joanie:  Seems like the proper way works now.
            # Leaving the above in for now until we know for certain.
            #
            row = parent.table.getRowAtIndex(obj.index)
            col = parent.table.getColumnAtIndex(obj.index)
            return [row, col]

        return [0, 0]

    def isHeader(self, obj):
        """Returns True if the table cell is a header"""

        if obj.attributes:
            for attribute in obj.attributes:
                if attribute == "tag:TH":
                    return True

    def getRowHeader(self, obj):
        """Returns the row header of a ROLE_TABLE_CELL or None if the
        header cannot be found.
        """

        rowHeader = None
        parent = obj.parent
        if parent and parent.table:
            [row, col] = self.getCellCoordinates(obj)
            # Theoretically, we should be able to quickly get the text
            # of a {row, column}Header via get{Row,Column}Description().
            # Mozilla doesn't expose the information that way, however.
            # get{Row, Column}Header seems to work sometimes.
            #
            accRowHeader = parent.table.getRowHeader(row)
            if accRowHeader:
                rowHeader = atspi.Accessible.makeAccessible(accRowHeader)
                rowHeader = rowHeader.text.getText(0, -1)

            # Headers that are strictly marked up with <th> do not seem
            # to be exposed through get{Row, Column}Header.
            #
            else:
                for col in range(0, parent.table.nColumns - 1):
                    accCell = parent.table.getAccessibleAt(row, col)
                    cell = atspi.Accessible.makeAccessible(accCell)
                    if self.isHeader(cell) and cell.text:
                        rowHeader = cell.text.getText(0, -1)
                        break

        return rowHeader

    def getColumnHeader(self, obj):
        """Returns the column header of a ROLE_TABLE_CELL or None if the
        header cannot be found.
        """

        colHeader = None
        parent = obj.parent
        if parent and parent.table:
            [row, col] = self.getCellCoordinates(obj)
            # Theoretically, we should be able to quickly get the text
            # of a {row, column}Header via get{Row,Column}Description().
            # Mozilla doesn't expose the information that way, however.
            # If the column header is in a <thead>, we can get it with
            # getColumnHeader.
            #
            accColHeader = parent.table.getColumnHeader(col)
            if accColHeader:
                colHeader = atspi.Accessible.makeAccessible(accColHeader)
                colHeader = colHeader.text.getText(0, -1)

            # Headers that are strictly marked up with <th> do not seem
            # to be exposed through get{Row, Column}Header.
            #
            else:
                for row in range(0, parent.table.nRows - 1):
                    accCell = parent.table.getAccessibleAt(row, col)
                    cell = atspi.Accessible.makeAccessible(accCell)
                    if self.isHeader(cell) and cell.text:
                        colHeader = cell.text.getText(0, -1)
                        break

        return colHeader

    def getTableCaption(self, obj):
        """Returns the ROLE_CAPTION object of a ROLE_TABLE object or None
        if the caption cannot be found.
        """
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child and (child.role == rolenames.ROLE_CAPTION):
                return child
        return None

    def getLinkBasename(self, obj):
        """Returns the relevant information from the URI.  The idea is
        to attempt to strip off all prefix and suffix, much like the
        basename command in a shell."""

        basename = None

        if obj and obj.hyperlink:
            uri = obj.hyperlink.getURI(0)
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

                    # Now, try to strip off the suffixes.
                    #
                    basename = basename.split('.')[0]
                    basename = basename.split('?')[0]
                    basename = basename.split('#')[0]

        return basename

    def getContainingLink(self, obj):
        """Returns the link containing the given object, or None if the
        given object is not in a link."""

        if not obj:
            return None

        linkObj = None

        obj = obj.parent
        while obj and (obj != obj.parent):
            if obj.role == rolenames.ROLE_LINK:
                linkObj = obj
                break
            elif obj.role == rolenames.ROLE_DOCUMENT_FRAME:
                break
            else:
                obj = obj.parent

        return linkObj

    def isUselessObject(self, obj):
        """Returns true if the given object is an obj that doesn't
        have any meaning associated with it and it is not inside a
        link."""

        if not obj:
            return True

        useless = False

        if obj.role in [rolenames.ROLE_IMAGE, \
                        rolenames.ROLE_TABLE_CELL, \
                        rolenames.ROLE_SECTION]:
            text = self.getDisplayedText(obj)
            if (not text) or (len(text) == 0):
                text = self.getDisplayedLabel(obj)
                if (not text) or (len(text) == 0):
                    useless = True

        if useless:
            link = self.getContainingLink(obj)
            if link:
                useless = False

        return useless

    def isLayoutOnly(self, obj):
        """Returns True if the given object is a table and is for layout
        purposes only."""

        if self.isUselessObject(obj):
            debug.println(debug.LEVEL_FINEST,
                          "Object deemed to be useless: " \
                          + obj.toString("", True))
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
        if pursue and (obj.role == rolenames.ROLE_DOCUMENT_FRAME):
            documentFrame = self.getDocumentFrame()
            pursue = obj == documentFrame

        return pursue

    def getHeadingLevel(self, obj):
        """Determines the heading level of the given object.  A value
        of 0 means there is no heading level."""

        level = 0

        if obj.role == rolenames.ROLE_HEADING:
            attributes = obj.attributes
            for attribute in attributes:
                if attribute.startswith("level:"):
                    level = int(attribute.split(":")[1])
                    break

        return level

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

        if obj.text:
            unicodeText = self.getUnicodeText(obj)
            if characterOffset >= len(unicodeText):
                return [obj, -1]

            character = self.getText(obj,
                                     characterOffset,
                                     characterOffset + 1).decode("UTF-8")
            if character == self.EMBEDDED_OBJECT_CHARACTER:
                try:
                    childIndex = self.getChildIndex(obj, characterOffset)
                    return self.findFirstCaretContext(obj.child(childIndex), 0)
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

        if obj.text:
            unicodeText = self.getUnicodeText(obj)
            nextOffset = startOffset + 1
            if nextOffset < len(unicodeText):
                if unicodeText[nextOffset] != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, nextOffset]
                elif obj.childCount:
                    child = obj.child(self.getChildIndex(obj, nextOffset))
                    if child:
                        return self.findNextCaretInOrder(child,
                                                         -1,
                                                         includeNonText)
        elif obj.childCount and obj.child(0):
            try:
                return self.findNextCaretInOrder(obj.child(0),
                                                 -1,
                                                 includeNonText)
            except:
                debug.printException(debug.LEVEL_SEVERE)
        elif includeNonText and (startOffset < 0) \
            and (not self.isLayoutOnly(obj)):
            extents = obj.extents
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findNextCaretInOrder(obj.parent,
                                                 characterOffsetInParent,
                                                 includeNonText)
            else:
                index = obj.index + 1
                if index < obj.parent.childCount:
                    try:
                        return self.findNextCaretInOrder(
                            obj.parent.child(index),
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

        if obj.text:
            unicodeText = self.getUnicodeText(obj)
            if startOffset == -1:
                startOffset = len(unicodeText)
            previousOffset = startOffset - 1
            if previousOffset >= 0:
                if unicodeText[previousOffset] \
                    != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, previousOffset]
                else:
                    return self.findPreviousCaretInOrder(
                        obj.child(self.getChildIndex(obj, previousOffset)),
                        -1,
                        includeNonText)
        elif obj.childCount and obj.child(obj.childCount - 1):
            try:
                return self.findPreviousCaretInOrder(
                    obj.child(obj.childCount - 1),
                    -1,
                    includeNonText)
            except:
                debug.printException(debug.LEVEL_SEVERE)
        elif includeNonText and (startOffset < 0) \
            and (not self.isLayoutOnly(obj)):
            extents = obj.extents
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findPreviousCaretInOrder(obj.parent,
                                                     characterOffsetInParent,
                                                     includeNonText)
            else:
                index = obj.index - 1
                if index >= 0:
                    try:
                        return self.findPreviousCaretInOrder(
                            obj.parent.child(index),
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

        index = obj.index - 1
        if (index < 0) and (obj.role != rolenames.ROLE_DOCUMENT_FRAME):
            previousObj = obj.parent
        else:
            # [[[TODO: HACK - WDW defensive programming because Gecko
            # ally hierarchies are not always working.  Objects say
            # they have children, but these children don't exist when
            # we go to get them.  So...we'll just keep going backwards
            # until we find a real child that we can work with.]]]
            #
            while not isinstance(previousObj, atspi.Accessible) \
                and index >= 0:
                previousObj = obj.parent.child(index)
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
                if obj.role != rolenames.ROLE_DOCUMENT_FRAME:
                    previousObj = obj.parent
            else:
                while previousObj.childCount:
                    index = previousObj.childCount - 1
                    while index >= 0:
                        child = previousObj.child(index)
                        if isinstance(child, atspi.Accessible):
                            previousObj = child
                            break
                        else:
                            index -= 1
                    if index < 0:
                        break

        return previousObj

    def findNextObject(self, obj):
        """Finds the object after to this one, where the tree we're
        dealing with is a DOM and 'next' means the next object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        """

        nextObj = None

        # If the object has children, we'll choose the first one.
        #
        # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
        # a bit of a challenge.]]]
        #
        index = 0
        while index < obj.childCount:
            child = obj.child(index)
            if isinstance(child, atspi.Accessible):
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
            index = obj.index + 1
            while index < obj.parent.childCount:
                child = obj.parent.child(index)
                if isinstance(child, atspi.Accessible):
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
            while (candidate.index >= (candidate.parent.childCount - 1)) \
                and (candidate.role != rolenames.ROLE_DOCUMENT_FRAME):
                candidate = candidate.parent

            # Now...let's get the sibling.
            #
            # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
            # a bit of a challenge.]]]
            #
            if candidate.role != rolenames.ROLE_DOCUMENT_FRAME:
                index = candidate.index + 1
                while index < candidate.parent.childCount:
                    child = candidate.parent.child(index)
                    if isinstance(child, atspi.Accessible):
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

    def findPreviousRole(self, roles):
        """Finds the caret offset at the beginning of the next object
        using the given roles list as a pattern to match.

        Arguments:
        -roles: a list of roles from rolenames.py
        """

        [currentObj, characterOffset] = self.getCaretContext()

        ancestors = []
        nestableRoles = [rolenames.ROLE_LIST, rolenames.ROLE_TABLE]
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        obj = self.findPreviousObject(currentObj)
        while obj:
            isNestedItem = ((obj != currentObj.parent) \
                            and (currentObj.parent.role == obj.role) \
                            and (obj.role in nestableRoles))
            if ((not obj in ancestors) or isNestedItem) \
               and (obj.role in roles) \
               and (not self.isLayoutOnly(obj)):
                return self.findFirstCaretContext(obj, 0)
            else:
                obj = self.findPreviousObject(obj)

        return [None, -1]

    def findNextRole(self, roles):
        """Finds the caret offset at the beginning of the next object
        using the given roles list as a pattern to match or not match.

        Arguments:
        -roles: a list of roles from rolenames.py
        -match: if True, the found object will have a role from roles;
                if False, the found object will not have a role from roles
        """

        [currentObj, characterOffset] = self.getCaretContext()

        ancestors = []
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        obj = self.findNextObject(currentObj)
        while obj:
            if (not obj in ancestors) and (obj.role in roles) \
                and (not self.isLayoutOnly(obj)):
                return self.findFirstCaretContext(obj, 0)
            else:
                obj = self.findNextObject(obj)

        return [None, -1]

    ####################################################################
    #                                                                  #
    # Methods to get information about current object.                 #
    #                                                                  #
    ####################################################################

    def getCaretContext(self, includeNonText=True):
        """Returns the current [obj, caretOffset] if defined.  If not,
        it returns the first [obj, caretOffset] found by an in order
        traversal from the beginning of the document."""

        try:
            return self.caretContext
        except:
            self.caretContext = self.findNextCaretInOrder(None,
                                                          -1,
                                                          includeNonText)
        return self.caretContext

    def getCharacterAtOffset(self, obj, characterOffset):
        """Returns the character at the given characterOffset in the
        given object or None if the object does not implement the
        accessible text specialization.
        """
        if obj and obj.text:
            unicodeText = self.getUnicodeText(obj)
            return unicodeText[characterOffset].encode("UTF-8")
        else:
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
            if not obj.text:
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
            if not obj.text:
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

        # If we're looking for the current word, we'll search
        # backwards to the beginning the current line and then
        # forwards to the beginning of the next line.
        #
        contents = []

        lineExtents = self.getExtents(
            obj, characterOffset, characterOffset + 1)

        [lastObj, lastCharacterOffset] = [obj, characterOffset]
        while obj:
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
                if not self.onSameLine(extents, lineExtents):
                    break
                elif (lastObj == obj) and len(contents):
                    contents[-1][2] = characterOffset + 1
                else:
                    contents.append([obj,
                                     characterOffset,
                                     characterOffset + 1])
                lineExtents = self.getBoundary(lineExtents, extents)
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

        #if not obj.state.count(atspi.Accessibility.STATE_SHOWING):
        #    return [[None, -1, -1]]

        if not obj.text:
            return [[obj, -1, -1]]

        contents = []
        text = self.getUnicodeText(obj)
        for offset in range(characterOffset, len(text)):
            if text[offset] == self.EMBEDDED_OBJECT_CHARACTER:
                contents.extend(self.getObjectContentsAtOffset(
                    obj.child(self.getChildIndex(obj, offset)),
                    0))
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
        if obj.role == rolenames.ROLE_LINK:
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
            # get the label via a speech generator.
            #
            if self.isLabellingContents(obj, contents):
                continue

            if obj.text:
                strings = [self.getText(obj, startOffset, endOffset)]
                if not obj.role in [rolenames.ROLE_DOCUMENT_FRAME,
                                    rolenames.ROLE_TABLE_CELL]:
                    strings.extend(\
                        self.speechGenerator._getSpeechForObjectRole(obj))

            elif self.isLayoutOnly(obj):
                continue
            else:
                strings = self.speechGenerator.getSpeech(obj, False)

            for string in strings:
                utterances.append([string, self.getACSS(obj, string)])

            if obj.role == rolenames.ROLE_HEADING:
                level = self.getHeadingLevel(obj)
                if level:
                    utterances.append([" ", self.getACSS(obj, " ")])
                    utterances.append([_("level %d") % level, None])

        return utterances

    def speakContents(self, contents):
        utterances = self.getUtterancesFromContents(contents)

        # Now...clump utterances together by acss.
        #
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
                speech.speak(_("blank"), clumped[0][1], False)
        else:
            for [string, acss] in clumped:
                speech.speak(string, acss, False)

    def speakCharacterAtOffset(self, obj, characterOffset):
        """Speaks the character at the given characterOffset in the
        given object."""
        character = self.getCharacterAtOffset(obj, characterOffset)
        if obj:
            if character:
                speech.speak(character, self.getACSS(obj, character), False)
            else:
                # We'll run into this when we hit a component with no
                # text, such as a checkbox.  In these cases, we'll
                # just speak the entire component.
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

        self.caretContext = [obj, characterOffset]

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
            objectForFocus = obj
            while objectForFocus and obj:
                if objectForFocus.state.count(\
                    atspi.Accessibility.STATE_FOCUSABLE):
                    break
                else:
                    objectForFocus = objectForFocus.parent

            if objectForFocus:
                # [[[See https://bugzilla.mozilla.org/show_bug.cgi?id=363214.
                # We need to set focus on the parent of the document frame.]]]
                #
                # [[[WDW - additional note - just setting focus on the
                # first focusable object seems to do the trick, so we
                # won't follow the advice from 363214.  Besides, if we
                # follow that advice, it doesn't work.]]]
                #
                #if objectForFocus.role == rolenames.ROLE_DOCUMENT_FRAME:
                #    objectForFocus = objectForFocus.parent
                focusGrabbed = objectForFocus.component.grabFocus()

        # If there is a character there, we'd like to position the
        # caret the right spot.  [[[TODO: WDW - numbered lists are
        # whacked in that setting the caret offset somewhere in
        # the number will end up positioning the caret at the end
        # of the list.]]]
        #
        character = self.getCharacterAtOffset(obj, characterOffset)
        if character:
            if obj.role != rolenames.ROLE_LIST_ITEM:
                caretSet = obj.text.setCaretOffset(characterOffset)
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
            if obj and obj.state.count(atspi.Accessibility.STATE_SHOWING):
                break
        if obj:
            self.setCaretPosition(obj, characterOffset)
        else:
            del self.caretContext

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
            if obj and obj.state.count(atspi.Accessibility.STATE_SHOWING):
                break

        if obj:
            self.setCaretPosition(obj, characterOffset)
        else:
            del self.caretContext

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

    def goPreviousLine(self, inputEvent):
        """Positions the caret offset at the previous line in the
        document window, attempting to preserve horizontal caret
        position.
        """
        [obj, characterOffset] = self.getCaretContext()
        lineExtents = self.getExtents(
            obj, characterOffset, characterOffset + 1)
        try:
            characterExtents = self.targetCharacterExtents
        except:
            characterExtents = lineExtents

        #print "GPL STARTING AT", obj.role, characterOffset

        crossedLineBoundary = False
        [lastObj, lastCharacterOffset] = [obj, characterOffset]
        while obj:
            extents = self.getExtents(
                obj, characterOffset, characterOffset + 1)
            if obj.text:
                if characterOffset > 0:
                    previousChar = \
                        obj.text.getText(characterOffset - 1, characterOffset)
                else:
                    previousChar = None
                currentChar = obj.text.getText(characterOffset,
                                               characterOffset + 1)
            else:
                previousChar = None
                currentChar = None

            #print "GPL LOOKING AT", obj.role, extents

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
                        lineExtents = extents
                        if currentChar != "\n":
                            crossedLineBoundary = True
                        elif previousChar == "\n":
                            crossedLineBoundary = True
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

        #print "GPL ENDED UP AT", lastObj.role, lineExtents

        contents = self.getLineContentsAtOffset(lastObj,
                                                lastCharacterOffset)

        if not len(contents):
            return

        if arrowToLineBeginning:
            [lastObj, lastCharacterOffset, endOffset] = contents[0]

        self.setCaretPosition(lastObj, lastCharacterOffset)
        self.updateBraille(lastObj)
        self.speakContents(contents)

        # Debug...
        #
        #contents = self.getLineContentsAtOffset(lastObj, lastCharacterOffset)
        #self.dumpContents(inputEvent, contents)

    def goNextLine(self, inputEvent):
        """Positions the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.
        """
        [obj, characterOffset] = self.getCaretContext()
        lineExtents = self.getExtents(
            obj, characterOffset, characterOffset + 1)
        try:
            characterExtents = self.targetCharacterExtents
        except:
            characterExtents = lineExtents

        #print "GNL STARTING AT", obj.role, characterOffset

        crossedLineBoundary = False
        [lastObj, lastCharacterOffset] = [obj, characterOffset]
        while obj:
            extents = self.getExtents(
                obj, characterOffset, characterOffset + 1)
            if obj.text:
                if characterOffset > 0:
                    previousChar = \
                        obj.text.getText(characterOffset - 1, characterOffset)
                else:
                    previousChar = None
                currentChar = \
                        obj.text.getText(characterOffset, characterOffset + 1)
            else:
                previousChar = None
                currentChar = None

            #print "GNL LOOKING AT", obj.role, extents

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
                        lineExtents = extents
                        if currentChar != "\n":
                            crossedLineBoundary = True
                        elif previousChar == "\n":
                            crossedLineBoundary = True
                        if crossedLineBoundary and arrowToLineBeginning:
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

        #print "GNL ENDED UP AT", lastObj.role, lineExtents
        #print "GNL ENDED UP AT", lastObj
        #print "                ", lastObj.role, lastCharacterOffset
        #print "                '%s'" % self.getText(lastObj, 0, -1)
        #print "                '%s'" % self.getText(lastObj,
        #                                            lastCharacterOffset,
        #                                            lastCharacterOffset + 1)

        self.setCaretPosition(lastObj, lastCharacterOffset)
        self.updateBraille(lastObj)
        self.speakContents(self.getLineContentsAtOffset(lastObj,
                                                        lastCharacterOffset))
        # Debug...
        #
        #contents = self.getLineContentsAtOffset(lastObj, lastCharacterOffset)
        #self.dumpContents(inputEvent, contents)

    def goPreviousHeading(self, inputEvent):
        [obj, characterOffset] = self.findPreviousRole(
            [rolenames.ROLE_HEADING])
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more headings."))

    def goNextHeading(self, inputEvent):
        [obj, characterOffset] = self.findNextRole([rolenames.ROLE_HEADING])
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more headings."))

    def goPreviousHeadingAtLevel(self, inputEvent, desiredLevel):
        found = False
        level = 0
        [obj, characterOffset] = self.getCaretContext()
        if obj.parent.role == rolenames.ROLE_HEADING:
            obj = obj.parent
        while obj and not found:
            obj = self.findPreviousObject(obj)
            if obj and (obj.role == rolenames.ROLE_HEADING):
                level = self.getHeadingLevel(obj)
                if level == desiredLevel:
                    found = True
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more headings at level %d.") % desiredLevel)

    def goNextHeadingAtLevel(self, inputEvent, desiredLevel):
        found = False
        level = 0
        [obj, characterOffset] = self.getCaretContext()
        while obj and not found:
            obj = self.findNextObject(obj)
            if obj and (obj.role == rolenames.ROLE_HEADING):
                level = self.getHeadingLevel(obj)
                if level == desiredLevel:
                    found = True
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more headings at level %d.") % desiredLevel)

    def goNextHeading1(self, inputEvent):
        self.goNextHeadingAtLevel(inputEvent, 1)

    def goPreviousHeading1(self, inputEvent):
        self.goPreviousHeadingAtLevel(inputEvent, 1)

    def goNextHeading2(self, inputEvent):
        self.goNextHeadingAtLevel(inputEvent, 2)

    def goPreviousHeading2(self, inputEvent):
        self.goPreviousHeadingAtLevel(inputEvent, 2)

    def goNextHeading3(self, inputEvent):
        self.goNextHeadingAtLevel(inputEvent, 3)

    def goPreviousHeading3(self, inputEvent):
        self.goPreviousHeadingAtLevel(inputEvent, 3)

    def goNextHeading4(self, inputEvent):
        self.goNextHeadingAtLevel(inputEvent, 4)

    def goPreviousHeading4(self, inputEvent):
        self.goPreviousHeadingAtLevel(inputEvent, 4)

    def goNextHeading5(self, inputEvent):
        self.goNextHeadingAtLevel(inputEvent, 5)

    def goPreviousHeading5(self, inputEvent):
        self.goPreviousHeadingAtLevel(inputEvent, 5)

    def goNextHeading6(self, inputEvent):
        self.goNextHeadingAtLevel(inputEvent, 6)

    def goPreviousHeading6(self, inputEvent):
        self.goPreviousHeadingAtLevel(inputEvent, 6)

    def goPreviousChunk(self, inputEvent):
        [obj, characterOffset] = self.findPreviousRole(OBJECT_ROLES)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more large objects."))

    def goNextChunk(self, inputEvent):
        [obj, characterOffset] = self.findNextRole(OBJECT_ROLES)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more large objects."))

    def goPreviousList(self, inputEvent):
        [obj, characterOffset] = self.findPreviousRole([rolenames.ROLE_LIST])
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            parent = obj.parent
            while parent.role != rolenames.ROLE_LIST:
                parent = parent.parent
            nItems = 0
            for i in range(0, parent.childCount):
                if parent.child(i).role == rolenames.ROLE_LIST_ITEM:
                    nItems += 1
            itemString = ngettext("List with %d item",
                                  "List with %d items",
                                  nItems) % nItems
            speech.speak(itemString)
            nestingLevel = 0
            while parent.parent.role == rolenames.ROLE_LIST:
                nestingLevel += 1
                parent = parent.parent
            if nestingLevel:
                speech.speak(_("Nesting level %d") % nestingLevel)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more lists."))

    def goNextList(self, inputEvent):
        [obj, characterOffset] = self.findNextRole([rolenames.ROLE_LIST])
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            parent = obj.parent
            while parent.role != rolenames.ROLE_LIST:
                parent = parent.parent
            nItems = 0
            for i in range(0, parent.childCount):
                if parent.child(i).role == rolenames.ROLE_LIST_ITEM:
                    nItems += 1
            itemString = ngettext("List with %d item",
                                  "List with %d items",
                                  nItems) % nItems
            speech.speak(itemString)
            nestingLevel = 0
            while parent.parent.role == rolenames.ROLE_LIST:
                nestingLevel += 1
                parent = parent.parent
            if nestingLevel:
                speech.speak(_("Nesting level %d") % nestingLevel)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more lists."))

    def goPreviousListItem(self, inputEvent):
        [obj, characterOffset] = self.findPreviousRole(
            [rolenames.ROLE_LIST_ITEM])
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more list items."))

    def goNextListItem(self, inputEvent):
        [obj, characterOffset] = self.findNextRole([rolenames.ROLE_LIST_ITEM])
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getLineContentsAtOffset(obj,
                                                            characterOffset))
        else:
            speech.speak(_("No more list items."))

    def goPreviousUnvisitedLink(self, inputEvent):
        # If the currentObject has a link in its ancestry, we've
        # already started out on a link and need to move off of
        # it else we'll get stuck.
        #
        [currentObj, characterOffset] = self.getCaretContext()
        containingLink = self.getContainingLink(currentObj)
        if containingLink:
            obj = self.findPreviousObject(containingLink)
        else:
            obj = self.findPreviousObject(currentObj)

        while obj and \
              (obj.role != rolenames.ROLE_LINK or \
               (obj.role == rolenames.ROLE_LINK and \
                obj.state.count(atspi.Accessibility.STATE_VISITED))):
            obj = self.findPreviousObject(obj)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more unvisited links."))

    def goNextUnvisitedLink(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        obj = self.findNextObject(obj)
        while obj and \
              (obj.role != rolenames.ROLE_LINK or \
               (obj.role == rolenames.ROLE_LINK and \
                obj.state.count(atspi.Accessibility.STATE_VISITED))):
            obj = self.findNextObject(obj)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more unvisited links."))

    def goPreviousVisitedLink(self, inputEvent):
        # If the currentObject has a link in its ancestry, we've
        # already started out on a link and need to move off of
        # it else we'll get stuck.
        #
        [currentObj, characterOffset] = self.getCaretContext()
        containingLink = self.getContainingLink(currentObj)
        if containingLink:
            obj = self.findPreviousObject(containingLink)
        else:
            obj = self.findPreviousObject(currentObj)

        while obj and \
              (obj.role != rolenames.ROLE_LINK or not \
               obj.state.count(atspi.Accessibility.STATE_VISITED)):
            obj = self.findPreviousObject(obj)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more visited links."))

    def goNextVisitedLink(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        obj = self.findNextObject(obj)
        while obj and \
              (obj.role != rolenames.ROLE_LINK or not \
               obj.state.count(atspi.Accessibility.STATE_VISITED)):
            obj = self.findNextObject(obj)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more visited links."))

    def goPreviousTable(self, inputEvent):
        [obj, characterOffset] = self.findPreviousRole([rolenames.ROLE_TABLE])
        if obj:
            nRows = obj.table.nRows
            nColumns = obj.table.nColumns
            rowString = ngettext("Table with %d row",
                                 "Table with %d rows",
                                  nRows) % nRows
            colString = ngettext(" and %d column",
                                 " and %d columns",
                                  nColumns) % nColumns
            speech.speak(rowString + colString)
            caption = self.getTableCaption(obj)
            if caption and caption.text:
                speech.speak(caption.text.getText(0, -1))
            cell = obj.table.getAccessibleAt(0, 0)
            obj = atspi.Accessible.makeAccessible(cell)
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            contents = self.getObjectContentsAtOffset(obj, characterOffset)
            firstCellContents = contents[0][0].text
            if firstCellContents:
                self.speakContents(contents)
            else:
                speech.speak(_("blank"))
        else:
            speech.speak(_("No more tables."))

    def goNextTable(self, inputEvent):
        [obj, characterOffset] = self.findNextRole([rolenames.ROLE_TABLE])
        if obj:
            nRows = obj.table.nRows
            nColumns = obj.table.nColumns
            rowString = ngettext("Table with %d row",
                                 "Table with %d rows",
                                  nRows) % nRows
            colString = ngettext(" and %d column",
                                 " and %d columns",
                                  nColumns) % nColumns
            speech.speak(rowString + colString)
            caption = self.getTableCaption(obj)
            if caption and caption.text:
                speech.speak(caption.text.getText(0, -1))
            cell = obj.table.getAccessibleAt(0, 0)
            obj = atspi.Accessible.makeAccessible(cell)
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            contents = self.getObjectContentsAtOffset(obj, characterOffset)
            firstCellContents = contents[0][0].text
            if firstCellContents:
                self.speakContents(contents)
            else:
                speech.speak(_("blank"))
        else:
            speech.speak(_("No more tables."))

    def goCellLeft(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        while obj and (obj != obj.parent) and \
              (obj.role != rolenames.ROLE_TABLE_CELL):
            obj = obj.parent
        if obj and (obj.role == rolenames.ROLE_TABLE_CELL):
            [row, col] = self.getCellCoordinates(obj)
            if col > 0:
                cell = obj.parent.table.getAccessibleAt(row, col - 1)
                obj = atspi.Accessible.makeAccessible(cell)
                [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
                colHeader = self.getColumnHeader(obj)
                if colHeader and not self.isHeader(obj):
                    speech.speak(colHeader)
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents( \
                        self.getObjectContentsAtOffset(obj, characterOffset))
            else:
                speech.speak(_("Beginning of row."))
        else:
            speech.speak(_("Not in a table."))

    def goCellRight(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        while obj and (obj != obj.parent) and \
              (obj.role != rolenames.ROLE_TABLE_CELL):
            obj = obj.parent
        if obj and (obj.role == rolenames.ROLE_TABLE_CELL):
            [row, col] = self.getCellCoordinates(obj)
            if col < obj.parent.table.nColumns - 1:
                cell = obj.parent.table.getAccessibleAt(row, col + 1)
                obj = atspi.Accessible.makeAccessible(cell)
                colHeader = self.getColumnHeader(obj)
                if colHeader and not self.isHeader(obj):
                    speech.speak(colHeader)
                [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents( \
                        self.getObjectContentsAtOffset(obj, characterOffset))
            else:
                speech.speak(_("End of row."))
        else:
            speech.speak(_("Not in a table."))

    def goCellUp(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        while obj and (obj != obj.parent) and \
              (obj.role != rolenames.ROLE_TABLE_CELL):
            obj = obj.parent
        if obj and (obj.role == rolenames.ROLE_TABLE_CELL):
            [row, col] = self.getCellCoordinates(obj)
            if row > 0:
                cell = obj.parent.table.getAccessibleAt(row - 1, col)
                obj = atspi.Accessible.makeAccessible(cell)
                rowHeader = self.getRowHeader(obj)
                if rowHeader and not self.isHeader(obj):
                    speech.speak(rowHeader)
                [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents( \
                        self.getObjectContentsAtOffset(obj, characterOffset))
            else:
                speech.speak(_("Top of column."))
        else:
            speech.speak(_("Not in a table."))

    def goCellDown(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        while obj and (obj != obj.parent) and \
              (obj.role != rolenames.ROLE_TABLE_CELL):
            obj = obj.parent
        if obj and (obj.role == rolenames.ROLE_TABLE_CELL):
            [row, col] = self.getCellCoordinates(obj)
            if row < obj.parent.table.nRows - 1:
                cell = obj.parent.table.getAccessibleAt(row + 1, col)
                obj = atspi.Accessible.makeAccessible(cell)
                rowHeader = self.getRowHeader(obj)
                if rowHeader and not self.isHeader(obj):
                    speech.speak(rowHeader)
                [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents( \
                        self.getObjectContentsAtOffset(obj, characterOffset))
            else:
                speech.speak(_("Bottom of column."))
        else:
            speech.speak(_("Not in a table."))

    def goCellFirst(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        while obj and (obj != obj.parent) and \
              (obj.role != rolenames.ROLE_TABLE):
            obj = obj.parent
        if obj and (obj.role == rolenames.ROLE_TABLE):
            cell = obj.table.getAccessibleAt(0, 0)
            obj = atspi.Accessible.makeAccessible(cell)
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            if obj:
                [row, col] = self.getCellCoordinates(obj)
                speech.speak(_("Row %d, column %d.") % (row + 1, col + 1))
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents( \
                        self.getObjectContentsAtOffset(obj, characterOffset))

        else:
            speech.speak(_("Not in a table."))

    def goCellLast(self, inputEvent):
        [obj, characterOffset] = self.getCaretContext()
        while obj and (obj != obj.parent) and \
              (obj.role != rolenames.ROLE_TABLE):
            obj = obj.parent
        if obj and (obj.role == rolenames.ROLE_TABLE):
            cell = obj.table.getAccessibleAt(obj.table.nRows - 1,
                                             obj.table.nColumns - 1)
            obj = atspi.Accessible.makeAccessible(cell)
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            if obj:
                [row, col] = self.getCellCoordinates(obj)
                speech.speak(_("Row %d, column %d.") % (row + 1, col + 1))
                self.setCaretPosition(obj, characterOffset)
                self.updateBraille(obj)
                self.speakContents( \
                        self.getObjectContentsAtOffset(obj, characterOffset))

        else:
            speech.speak(_("Not in a table."))

    def toggleCaretNavigation(self, inputEvent):
        """Toggles between Firefox native and Orca caret navigation."""

        global controlCaretNavigation

        if controlCaretNavigation:
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.removeByHandler(keyBinding.handler)
            controlCaretNavigation = False
            string = "Gecko is controlling the caret."
        else:
            controlCaretNavigation = True
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.add(keyBinding)
            string = "Orca is controlling the caret."

        debug.println(debug.LEVEL_CONFIGURATION, string)
        speech.speak(string)
        braille.displayMessage(string)
