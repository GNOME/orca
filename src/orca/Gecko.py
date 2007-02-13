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
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
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
import util

from orca_i18n import _

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
                rolenames.ROLE_IMAGE,
                rolenames.ROLE_LABEL,
                rolenames.ROLE_LIST_ITEM,
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
                rolenames.ROLE_SECTION,
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
            text = util.appendString(text, util.getDisplayedLabel(obj))
            text = util.appendString(text, util.getDisplayedText(obj))
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
                text = util.appendString(text, obj.name)

        if obj.state.count(atspi.Accessibility.STATE_CHECKED):
            text = util.appendString(text, "<x>")
        else:
            text = util.appendString(text, "< >")

        text = util.appendString(text, self._getTextForRole(obj))

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
        # class - we'll give this thing a name here.
        #
        label = util.getDisplayedLabel(parent)
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
        label = util.getDisplayedLabel(obj)
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

        self._debugGenerator("Gecko._getBrailleRegionsForImage", obj)

        regions = []

        text = ""
        text = util.appendString(text, util.getDisplayedLabel(obj))
        text = util.appendString(text, util.getDisplayedText(obj))

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
            text = util.appendString(text, self._getTextForRole(link))

        text = util.appendString(text, self._getTextForValue(obj))
        text = util.appendString(text, self._getTextForRole(obj))

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]

    def _getBrailleRegionsForLink(self, obj):
        """Gets text to be displayed for the current object's name,
        role, and any accelerators.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForLink", obj)

        regions = []

        text = ""
        text = util.appendString(text, util.getDisplayedLabel(obj))
        text = util.appendString(text, util.getDisplayedText(obj))

        # If there's no text for the link, expose part of the
        # URI to the user.
        #
        if len(text) == 0:
            basename = self._script.getLinkBasename(obj)
            if basename:
                text = basename

        text = util.appendString(text, self._getTextForValue(obj))
        text = util.appendString(text, self._getTextForRole(obj))

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]

    def getBrailleRegions(self, obj, groupChildren=True):
        return braillegenerator.BrailleGenerator.getBrailleRegions(\
            self, obj, groupChildren)

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
        # class - we'll give this thing a name here.
        #
        label = util.getDisplayedLabel(parent)
        if not label or not len(label):
            label = parent.name
        utterances.append(label)

        utterances.extend(self._getSpeechForObjectRole(obj))

        [text, caretOffset, startOffset] = util.getTextLineAtCaret(obj)
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
        label = util.getDisplayedLabel(obj)
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
        """Gets a list of utterances to be spoken for the current
        object's name, role, and any accelerators.

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
        """Gets a list of utterances to be spoken for the current
        object's name, role, and any accelerators.

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
            # is that it util.py:getDisplayedText will end up coming
            # back to the children of an object for the text in the
            # children if an object's text contains an
            # EMBEDDED_OBJECT_CHARACTER.
            #
            if parent.text:
                displayedText = parent.text.getText(0, -1)
                unicodeText = displayedText.decode("UTF-8")
                if unicodeText \
                    and (len(unicodeText) == 1) \
                    and (unicodeText[0] == util.EMBEDDED_OBJECT_CHARACTER):
                    parent = parent.parent
                    continue

            # Finally, put in the text and label (if they exist)
            #
            text = util.getDisplayedText(parent)
            label = util.getDisplayedLabel(parent)
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
        # chunk, etc.).
        #
        self._structuralNavigationFunctions = \
            [Script.goNextHeading,
             Script.goPreviousHeading,
             Script.goNextChunk,
             Script.goPreviousChunk]

        if controlCaretNavigation:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Gecko.py is controlling the caret.")
        else:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Firefox is controlling the caret.")

        # We keep track of whether we're currently in the process of
        # loading a page.  Ideally, Gecko will let us know when a page
        # is being loaded by:
        #
        # Setting the BUSY state of the document frame.  We should get
        # a object:state-changed:busy event with a detail1 that tells
        # us if the frame is busy (detail1==1) or not (detail1==0).
        #
        # Sending us "document:load-complete", "document:reload", and
        # "document:load-stopped" events.
        #
        # We can also watch for value change events on the progress
        # bar to let us know how things are progressing.
        #
        self._loadingDocumentContent = False

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

        self.inputEventHandlers["goPreviousHeadingHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousHeading,
                "Goes to previous heading.")

        self.inputEventHandlers["goNextHeadingHandler"] = \
            input_event.InputEventHandler(
                Script.goNextHeading,
                "Goes to next heading.")

        self.inputEventHandlers["goPreviousChunkHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousChunk,
                "Goes to previous chunk.")

        self.inputEventHandlers["goNextChunkHandler"] = \
            input_event.InputEventHandler(
                Script.goNextChunk,
                "Goes to next chunk.")

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
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                0,
                self.inputEventHandlers["goNextCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                0,
                self.inputEventHandlers["goPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                self.inputEventHandlers["goNextWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                1 << atspi.Accessibility.MODIFIER_CONTROL,
                self.inputEventHandlers["goPreviousWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Up",
                0,
                0,
                self.inputEventHandlers["goPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                0,
                0,
                self.inputEventHandlers["goNextLineHandler"]))

        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        # NOTE: We include ALT in all the bindings below so as to not
        # conflict with menu and other mnemonics.

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                0,
                self.inputEventHandlers["goNextHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousChunkHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                (1 << atspi.Accessibility.MODIFIER_SHIFT \
                 | 1 << atspi.Accessibility.MODIFIER_ALT),
                0,
                self.inputEventHandlers["goNextChunkHandler"]))

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
        # own navigation and we also handle the EMBEDDED_OBJECT_CHARACTER.
        # But...if we're not in HTML content, we'll defer to the default
        # script.
        #
        if not self.inDocumentContent():
            default.Script.onCaretMoved(self, event)
            return

        self.caretContext = self.findFirstCaretContext(\
            event.source,
            event.source.text.caretOffset)
        [obj, characterOffset] = self.caretContext

        # If the user presses left or right, we'll set the target
        # column for up/down navigation by line.  The goal here is
        # to make sure the caret moves somewhat vertically when
        # going up/down by line versus jumping to the beginning of
        # the line.
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
        # caret context for the document frame.
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
            # focus: events.]]]
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
        linkIndex = util.getLinkIndex(event.source, text.caretOffset)

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
                    speech.stop()
                    speech.speak(_("Finished loading %s.") \
                                 % event.source.name)
                else:
                    self._loadingDocumentContent = False
                    speech.stop()
                    speech.speak(_("Finished loading."))
            return

        default.Script.onStateChanged(self, event)

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
            if event.source.text:
                caretOffset = event.source.text.caretOffset
            else:
                caretOffset = 0
            self.caretContext = self.findFirstCaretContext(event.source,
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

        """Speaks the character at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent():
            default.Script.updateBraille(self, obj, extraRegion)
            return

        if not obj:
            return

        braille.clear()
        line = braille.Line()
        braille.addLine(line)

        [focusedObj, focusedCharacterOffset] = self.getCaretContext()
        contents = self.getLineContentsAtOffset(focusedObj,
                                                focusedCharacterOffset)
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
            # display.]]]
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
                            rolenames.ROLE_PASSWORD_TEXT]:
                label = util.getDisplayedLabel(obj)
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
        util.drawOutline(x, y, width, height)

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
        util.drawOutline(extents[0], extents[1], extents[2], extents[3])

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
                return False
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
                        if text[offset] == util.EMBEDDED_OBJECT_CHARACTER:
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
                    == util.EMBEDDED_OBJECT_CHARACTER):
                index = -1
                for character in range(0, characterOffset + 1):
                    if unicodeText[character] \
                        == util.EMBEDDED_OBJECT_CHARACTER:
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

        # If there's no overlap, they are on different lines.  Keep in
        # mind "lowest" and "highest" mean visually on the screen, but
        # that the value is the y coordinate.
        #
        highestBottom = min(a[1] + a[3], b[1] + b[3])
        lowestTop     = max(a[1],        b[1])
        if lowestTop > highestBottom:
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
            row = obj.index / parent.table.nColumns
            col = obj.index % parent.table.nColumns
            return [row, col]

            # By the way, here's the proper way to do it, since we
            # cannot always depend upon the ordering of the children.
            # Easy if it works...
            #
            # row = parent.table.getRowAtIndex(obj.index)
            # col = parent.table.getColumnAtIndex(obj.index)
            # return [row, col]

        return [0, 0]

    def getCellHeaders(self, obj):
        """Returns the [rowHeader, colHeader] of a ROLE_TABLE_CELL or
        [None, None] if the headers cannot be found.
        """

        parent = obj.parent
        if parent and parent.table:
            [row, col] = self.getCellCoordinates(obj)
            rowHeader = parent.table.getRowDescription(row)
            colHeader = parent.table.getColumnDescription(col)
            return [rowHeader, colHeader]

        return [None, None]

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

        if obj.role in [rolenames.ROLE_IMAGE, rolenames.ROLE_TABLE_CELL]:
            text = util.getDisplayedText(obj)
            if (not text) or (len(text) == 0):
                text = util.getDisplayedLabel(obj)
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
            if character == util.EMBEDDED_OBJECT_CHARACTER:
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
                if extents == (0, 0, 0, 0):
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
                if unicodeText[nextOffset] != util.EMBEDDED_OBJECT_CHARACTER:
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
                    != util.EMBEDDED_OBJECT_CHARACTER:
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

    def findPreviousRole(self, roles, match=True):
        """Positions the caret offset at the beginning of the next object
        using the given roles list as a pattern to match or not match.

        Arguments:
        -roles: a list of roles from rolenames.py
        -match: if True, the found object will have a role from roles;
                if False, the found object will not have a role from roles
        """
        [currentObj, characterOffset] = self.getCaretContext()

        obj = currentObj
        while obj:
            [obj, characterOffset] = self.findPreviousCaretInOrder(
                obj, characterOffset)
            if obj and (obj != currentObj):
                if (match and (obj.role in roles)) \
                    or (not match and not (obj.role in roles)):
                    return [obj, characterOffset]

        return [None, -1]

    def findNextRole(self, roles, match=True):
        """Positions the caret offset at the beginning of the next object
        using the given roles list as a pattern to match or not match.

        Arguments:
        -roles: a list of roles from rolenames.py
        -match: if True, the found object will have a role from roles;
                if False, the found object will not have a role from roles
        """
        [currentObj, characterOffset] = self.getCaretContext()

        obj = currentObj
        while obj:
            [obj, characterOffset] = self.findNextCaretInOrder(
                obj, characterOffset)
            if obj and (obj != currentObj):
                if (match and (obj.role in roles)) \
                    or (not match and not (obj.role in roles)):
                    return [obj, characterOffset]

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
                if util.isWordDelimiter(character):
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
                if not util.isWordDelimiter(character):
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
            if text[offset] == util.EMBEDDED_OBJECT_CHARACTER:
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
        elif string and string.isupper():
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

            #print "GPL LOOKING AT", obj.role, extents

            # [[[TODO: WDW - HACK.  I think we end up with a zero
            # sized character when the accessible text implementation
            # of Gecko gives us whitespace that is not visible, but
            # is in the raw HTML source.  This should hopefully be
            # fixed at some point, but we just ignore it for now.
            #
            if extents != (0, 0, 0, 0):
                if not self.onSameLine(extents, lineExtents):
                    if not crossedLineBoundary:
                        lineExtents = extents
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

            #print "GNL LOOKING AT", obj.role, extents

            # [[[TODO: WDW - HACK.  I think we end up with a zero
            # sized character when the accessible text implementation
            # of Gecko gives us whitespace that is not visible, but
            # is in the raw HTML source.  This should hopefully be
            # fixed at some point, but we just ignore it for now.]]]
            #
            if extents != (0, 0, 0, 0):
                if not self.onSameLine(extents, lineExtents):
                    if not crossedLineBoundary:
                        lineExtents = extents
                        crossedLineBoundary = True
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

        #print "GNL ENDED UP AT", lastObj.role, lineExtents

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
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more headings."))

    def goNextHeading(self, inputEvent):
        [obj, characterOffset] = self.findNextRole([rolenames.ROLE_HEADING])
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more headings."))

    def goPreviousChunk(self, inputEvent):
        [obj, characterOffset] = self.findPreviousRole(OBJECT_ROLES)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more chunks."))

    def goNextChunk(self, inputEvent):
        [obj, characterOffset] = self.findNextRole(OBJECT_ROLES)
        if obj:
            [obj, characterOffset] = self.findFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.updateBraille(obj)
            self.speakContents(self.getObjectContentsAtOffset(obj,
                                                              characterOffset))
        else:
            speech.speak(_("No more chunks."))
