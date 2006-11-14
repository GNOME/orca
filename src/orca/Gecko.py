# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

"""Custom script for Gecko toolkit.  NOT WORKING WELL AT THE MOMENT."""

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
import orca
import orca_state
import rolenames
import settings
import speech
import speechgenerator
import util

from orca_i18n import _

# An embedded object character used to indicate that an object is
# embedded in a string.
#
# DETAIL: If an object presents text, it implements the accessible
# text interface.  If an object has children that also present
# information, then the accessible text for the object contains one
# EMBEDDED_OBJECT_CHARACTER for each child, where the
# EMBEDDED_OBJECT_CHARACTER represents the position of the child's
# text in the object and the order of the EMBEDDED_OBJECT_CHARACTERs
# represent the order of the children (i.e., the first
# EMBEDDED_OBJECT_CHARACTER represents child 0, the next
# EMBEDDED_OBJECT_CHARACTER represents child 1, and so on.)
#
EMBEDDED_OBJECT_CHARACTER = u'\ufffc'

# Roles that imply their text starts on a new line.
#
NEWLINE_ROLES = [rolenames.ROLE_PARAGRAPH,
                 rolenames.ROLE_SEPARATOR,
                 rolenames.ROLE_LIST_ITEM,
                 rolenames.ROLE_HEADING]

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

    def _getBrailleRegionsForAutocomplete(self, obj):
        """Gets the role of an autocomplete box.  We let the handlers
        for the children do the rest.

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

        # With Gecko, a combo box has a menu as a child.  If the menu
        # has a name (usually the case when the object is labelled by
        # something), then it is the text showing in the combo box.
        # If not, then the combo box is probably not labelled by
        # something.  If that's the case, then the name of the combo
        # box is the text that is showing.  Except perhaps if the
        # menu is popped up.  Then, the name is the name of the menu
        # item that is selected.
        #
        label = util.getDisplayedLabel(obj)
        menu = obj.child(0)

        focusedRegionIndex = 0
        if label and len(label):
            regions.append(braille.Region(label + " "))
            focusedRegionIndex = 1

        if menu.name:
            regions.append(braille.Region(menu.name))
        else:
            name = obj.name
            if menu.state.count(atspi.Accessibility.STATE_VISIBLE):
                selection = menu.selection
                item = selection.getSelectedChild(0)
                name = item.name
            regions.append(braille.Region(name))

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
        self.speechGenerators[rolenames.ROLE_ENTRY]        = \
             self._getSpeechForText

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

        # With Gecko, a combo box has a menu as a child.  If the menu
        # has a name (usually the case when the object is labelled by
        # something), then it is the text showing in the combo box.
        # If not, then the combo box is probably not labelled by
        # something.  If that's the case, then the name of the combo
        # box is the text that is showing.  Except perhaps if the
        # menu is popped up.  Then, the name is the name of the menu
        # item that is selected.
        #
        label = util.getDisplayedLabel(obj)
        menu = obj.child(0)

        if not already_focused and label:
            utterances.append(label)

        if not already_focused:
            utterances.extend(self._getSpeechForObjectRole(obj))

        if menu.name:
            utterances.append(menu.name)
        else:
            name = obj.name
            if menu.state.count(atspi.Accessibility.STATE_VISIBLE):
                selection = menu.selection
                item = selection.getSelectedChild(0)
                name = item.name
            utterances.append(name)

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForComboBox",
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
        - stopAncestor: the anscestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if not obj:
            return utterances

        if obj is stopAncestor:
            return utterances

        # We'll eliminate toolbars if we're in a menu.  The reason for
        # this is that Gecko puts its menu bar in a couple of nested
        # toolbars.
        #
        inMenuBar = False

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break

            if parent.role == rolenames.ROLE_MENU_BAR:
                inMenuBar = True

            # We try to omit things like fillers off the bat...
            #
            if (parent.role == rolenames.ROLE_FILLER) \
                or (parent.role == rolenames.ROLE_LIST_ITEM) \
                or (parent.role == rolenames.ROLE_LIST) \
                or (parent.role == rolenames.ROLE_PARAGRAPH) \
                or (parent.role == rolenames.ROLE_SECTION) \
                or (parent.role == rolenames.ROLE_LAYERED_PANE) \
                or (parent.role == rolenames.ROLE_SPLIT_PANE) \
                or (parent.role == rolenames.ROLE_SCROLL_PANE) \
                or (parent.role == rolenames.ROLE_UNKNOWN):
                parent = parent.parent
                continue

            text = util.getDisplayedText(parent)
            label = util.getDisplayedLabel(parent)

            # Don't announce unlabelled panels.
            #
            if parent.role == rolenames.ROLE_PANEL \
                and (((not label) or (len(label) == 0) \
                      or (not text) or (len(text) == 0))):
                parent = parent.parent
                continue

            # Skip table cells.
            #
            if parent.role == rolenames.ROLE_TABLE_CELL:
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
            utterances.append(rolenames.getSpeechForRoleName(parent))

            # Now...autocompletes are wierd.  We'll let the handling of
            # the entry give us the name.
            #
            if parent.role == rolenames.ROLE_AUTOCOMPLETE:
                parent = parent.parent
                continue

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
        self._caretNavigationFunctions = \
            [Script.goNextCharacter,
             Script.goPreviousCharacter,
             Script.goNextWord,
             Script.goPreviousWord,
             Script.goNextLine,
             Script.goPreviousLine]
        self._structuralNavigationFunctions = \
            [Script.goNextHeading,
             Script.goPreviousHeading]

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

        self.inputEventHandlers["dumpContentHandler"] = \
            input_event.InputEventHandler(
                Script.dumpContent,
                "Dumps document content.")

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

    def __getViBindings(self):
        """Returns an instance of keybindings.KeyBindings that use vi
        editor-style keys for navigating HTML content.
        """

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                (1 << settings.MODIFIER_ORCA
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["goNextCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                (1 << settings.MODIFIER_ORCA
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["goPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                (1 << settings.MODIFIER_ORCA
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                (1 << settings.MODIFIER_ORCA | \
                     1 << atspi.Accessibility.MODIFIER_CONTROL),
                self.inputEventHandlers["goNextWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                (1 << settings.MODIFIER_ORCA
                 | 1 << atspi.Accessibility.MODIFIER_CONTROL),
                (1 << settings.MODIFIER_ORCA | \
                     1 << atspi.Accessibility.MODIFIER_CONTROL),
                self.inputEventHandlers["goPreviousWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "j",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["goPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "k",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["goNextLineHandler"]))

        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                self.inputEventHandlers["goPreviousHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                1 << atspi.Accessibility.MODIFIER_SHIFT,
                0,
                self.inputEventHandlers["goNextHeadingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "d",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["dumpContentHandler"]))

        # [[[TODO: WDW - probably should make the choice of bindings a
        # setting and more customizable.  For now, it's just
        # experimental, so we hardcode things here.]]]
        #
        if False:
            for keyBinding in self.__getArrowBindings().keyBindings:
                keyBindings.add(keyBinding)
        else:
            for keyBinding in self.__getViBindings().keyBindings:
                keyBindings.add(keyBinding)

        return keyBindings

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """
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
                return self.useCaretNavigationModel()
            elif handler \
                and handler._function in self._structuralNavigationFunctions:
                return self.useStructuralNavigationModel()
            else:
                consumes = handler != None
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler and handler._function in self._caretNavigationFunctions:
                return self.useCaretNavigationModel()
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

        self.caretContext = self.getFirstCaretContext(\
            event.source,
            event.source.text.caretOffset)
        [obj, characterOffset] = self.caretContext

        # If the user presses left or right, we'll set the target
        # column for up/down navigation by line.  [[[TODO: WDW - this
        # should be bound more to the navigation function versus the
        # key that was pressed.  For example, if the vi editor-style
        # keys were used to move the caret, we should manage that as
        # well.]]]
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

        orca.setLocusOfFocus(event, event.source, False)
        default.Script.onCaretMoved(self, event)

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
           or (event.source.role == rolenames.ROLE_DOCUMENT_FRAME) \
           or (not len(event.source.role)):
            return

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
        #
        if event.source.role == rolenames.ROLE_AUTOCOMPLETE:
            entry = self.getAutocompleteEntry(event.source)
            orca.setLocusOfFocus(event, entry)
            return

        default.Script.onFocus(self, event)

    def onLinkSelected(self, event):
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

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
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
        else:
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
        contents = self.getLineAtOffset(focusedObj, focusedCharacterOffset)
        if not len(contents):
            return

        focusedRegion = None
        for content in contents:
            [obj, startOffset, endOffset] = content
            if not obj:
                continue

            if obj.text:
                string = self.getText(obj, startOffset, endOffset)
                if obj == focusedObj:
                    region = braille.Region(
                        string,
                        focusedCharacterOffset - startOffset)
                    if (focusedCharacterOffset >= startOffset) \
                       and (focusedCharacterOffset < endOffset):
                        focusedRegion = region
                else:
                    region = braille.Region(string)
            else:
                region = braille.Region(obj.name)
                if obj == focusedObj:
                    focusedRegion = region

            line.addRegion(region)

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
            # make sure we say something like "new line" or move the
            # caret context to the beginning of the next character via
            # a call to goNextWord.]]]
            #
            foo = self.getText(obj, 0, -1)
            if characterOffset >= len(foo):
                print "YIKES in Gecko.sayCharacter!"
                characterOffset -= 1

        self.presentCharacterAtOffset(obj, characterOffset)

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
            # make sure we say something like "new line" or move the
            # caret context to the beginning of the next word via
            # a call to goNextWord.]]]
            #
            foo = self.getText(obj, 0, -1)
            if characterOffset >= len(foo):
                print "YIKES in Gecko.sayWord!"
                characterOffset -= 1

        self.presentWordAtOffset(obj, characterOffset)

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
            # make sure we say something like "new line" or move the
            # caret context to the beginning of the next line via
            # a call to goNextLine.]]]
            #
            foo = self.getText(obj, 0, -1)
            if characterOffset >= len(foo):
                print "YIKES in Gecko.sayLine!"
                characterOffset -= 1
        self.presentLineAtOffset(obj, characterOffset)

    ####################################################################
    #                                                                  #
    # Utility Methods                                                  #
    #                                                                  #
    ####################################################################

    def getAutocompleteEntry(self, obj):
        """Returns the ROLE_ENTRY object of a ROLE_AUTOCOMPLETE object or
        None if the entry cannot be found.
        """
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child.role == rolenames.ROLE_ENTRY:
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
            row = parent.table.getRowAtIndex(obj.index)
            col = parent.table.getColumnAtIndex(obj.index)
            return [row, col]

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
            if child.role == rolenames.ROLE_CAPTION:
                return child
        return None

    def inDocumentContent(self):
        """Returns True if the current locus of focus is in the
        document content.
        """
        obj = orca_state.locusOfFocus
        while obj:
            if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
                return True
            else:
                obj = obj.parent
        return False

    def useCaretNavigationModel(self):
        """Returns True if we should do our own caret navigation.
        [[[TODO: WDW - this should return False if we're in something
        like an entry area or a list because we want their keyboard
        navigation stuff to work.]]]
        """

        # [[[WDW - disable this for now to see how far we can take
        # the Gecko navigation model.]]]
        #
        return False

        letThemDoItRoles = [rolenames.ROLE_ENTRY]
        obj = orca_state.locusOfFocus
        while obj:
            if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
                return True
            elif obj.role in letThemDoItRoles:
                return False
            else:
                obj = obj.parent
        return False

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation.
        [[[TODO: WDW - this should return False if we're in something
        like an entry area or a list because we want their keyboard
        navigation stuff to work.]]]
        """

        letThemDoItRoles = [rolenames.ROLE_ENTRY]
        obj = orca_state.locusOfFocus
        while obj:
            if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
                return True
            elif obj.role in letThemDoItRoles:
                return False
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
        # number 14 here represents something that seems to work well
        # with superscripts and subscripts on a line.
        #
        return abs(a[1] - b[1]) < 14

        highestBottom = min(a[1] + a[3], b[1] + b[3])
        lowestTop     = max(a[1],        b[1])

        # If we do overlap, lets see how much.  We'll require a 25% overlap
        # for now...
        #
        if lowestTop < highestBottom:
            overlapAmount = highestBottom - lowestTop
            shortestHeight = min(a[3], b[3])
            return ((1.0 * overlapAmount) / shortestHeight) > 0.25
        else:
            return False

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
            hyperlink = obj.hyperlink
            if obj.hyperlink:
                index = 0
                text = self.getUnicodeText(obj.parent)
                if text:
                    for offset in range(0, len(text)):
                        if text[offset] == EMBEDDED_OBJECT_CHARACTER:
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
            indeces = obj.childrenIndeces
        except:
            obj.childrenIndeces = {}

        try:
            return obj.childrenIndeces[characterOffset]
        except:
            obj.childrenIndeces[characterOffset] = -1
            unicodeText = self.getUnicodeText(obj)
            if unicodeText \
               and (unicodeText[characterOffset] == EMBEDDED_OBJECT_CHARACTER):
                index = -1
                for character in range(0, characterOffset + 1):
                    if unicodeText[character] == EMBEDDED_OBJECT_CHARACTER:
                        index += 1
                obj.childrenIndeces[characterOffset] = index

        return obj.childrenIndeces[characterOffset]

    def getNextCaretInOrder(self, obj=None,
                            startOffset=-1,
                            includeNonText=True):
        """Given an object an a character offset, return the next
        caret context following an in order traversal rule.

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

        #print "GO NEXT", obj, obj.role, startOffset

        if not obj:
            obj = self.getDocumentFrame()

        if obj.text:
            unicodeText = self.getUnicodeText(obj)
            nextOffset = startOffset + 1
            if nextOffset < len(unicodeText):
                if unicodeText[nextOffset] != EMBEDDED_OBJECT_CHARACTER:
                    return [obj, nextOffset]
                else:
                    return self.getNextCaretInOrder(
                        obj.child(self.getChildIndex(obj, nextOffset)),
                        -1,
                        includeNonText)
        elif obj.childCount:
            try:
                return self.getNextCaretInOrder(obj.child(0),
                                                -1,
                                                includeNonText)
            except:
                debug.printException(debug.LEVEL_SEVERE)
        elif includeNonText and (startOffset < 0):
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
                return self.getNextCaretInOrder(obj.parent,
                                                characterOffsetInParent,
                                                includeNonText)
            else:
                index = obj.index + 1
                if index < obj.parent.childCount:
                    try:
                        return self.getNextCaretInOrder(
                            obj.parent.child(index),
                            -1,
                            includeNonText)
                    except:
                        debug.printException(debug.LEVEL_SEVERE)
            obj = obj.parent

        return [None, -1]

    def getPreviousCaretInOrder(self,
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
                if unicodeText[previousOffset] != EMBEDDED_OBJECT_CHARACTER:
                    return [obj, previousOffset]
                else:
                    return self.getPreviousCaretInOrder(
                        obj.child(self.getChildIndex(obj, previousOffset)),
                        -1,
                        includeNonText)
        elif obj.childCount:
            try:
                return self.getPreviousCaretInOrder(
                    obj.child(obj.childCount - 1),
                    -1,
                    includeNonText)
            except:
                debug.printException(debug.LEVEL_SEVERE)
        elif includeNonText and (startOffset < 0):
            extents = obj.extents
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree
        #
        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        if obj.role == rolenames.ROLE_DOCUMENT_FRAME:
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.getPreviousCaretInOrder(obj.parent,
                                                    characterOffsetInParent,
                                                    includeNonText)
            else:
                index = obj.index - 1
                if index >= 0:
                    try:
                        return self.getPreviousCaretInOrder(
                            obj.parent.child(index),
                            -1,
                            includeNonText)
                    except:
                        debug.printException(debug.LEVEL_SEVERE)
            obj = obj.parent

        return [None, -1]

    def getFirstCaretContext(self, obj, characterOffset):
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
            character = self.getText(obj,
                                     characterOffset,
                                     characterOffset + 1).decode("UTF-8")
            if character == EMBEDDED_OBJECT_CHARACTER:
                try:
                    childIndex = self.getChildIndex(obj, characterOffset)
                    return self.getFirstCaretContext(obj.child(childIndex), 0)
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
                if extents == (0, 0, 0,0):
                    return self.getFirstCaretContext(obj, characterOffset + 1)
                else:
                    return [obj, characterOffset]
        else:
            return [obj, -1]

    def getCaretContext(self, includeNonText=True):
        """Returns the current [obj, caretOffset] if defined.  If not,
        it returns the first [obj, caretOffset] found by an in order
        traversal from the beginning of the document."""

        try:
            return self.caretContext
        except:
            self.caretContext = self.getNextCaretInOrder(None,
                                                         -1,
                                                         includeNonText)
        return self.caretContext

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

    def getLinearizedContents(self):
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

            [obj, characterOffset] = self.getNextCaretInOrder(obj,
                                                              characterOffset)

        return contents

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

    def presentString(self, obj, string, presentRole=False):
        if not obj or (not string and not presentRole):
            return
        if obj.role == rolenames.ROLE_LINK:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif string and string.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        if presentRole:
            ignoreRoles = [rolenames.ROLE_DOCUMENT_FRAME,
                           rolenames.ROLE_FORM,
                           rolenames.ROLE_PARAGRAPH,
                           rolenames.ROLE_SECTION,
                           rolenames.ROLE_TABLE_CELL]
            if not obj.role in ignoreRoles:
                string += " " + rolenames.getSpeechForRoleName(obj)

        if not len(string):
            return

        speech.speak(string, voice, False)

    def presentCharacterAtOffset(self, obj, characterOffset):
        self.presentString(obj,
                           self.getCharacterAtOffset(obj, characterOffset))

    def getWordAtOffset(self, obj, characterOffset):
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
                  self.getPreviousCaretInOrder(obj, characterOffset)

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
                  self.getNextCaretInOrder(obj, characterOffset)
            contents[-1][2] = lastCharacterOffset + 1

        return contents

    def presentWordAtOffset(self, obj, characterOffset):
        contents = self.getWordAtOffset(obj, characterOffset)
        if not len(contents):
            return
        [obj, startOffset, endOffset] = contents[0]
        if not obj:
            return
        if obj.text:
            string = self.getText(obj, startOffset, endOffset)
        else:
            string = obj.name
        self.presentString(obj, string, True)

    def getLineAtOffset(self, obj, characterOffset):
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
                  self.getPreviousCaretInOrder(obj, characterOffset)

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
                  self.getNextCaretInOrder(obj, characterOffset)

        return contents

    def presentLineAtOffset(self, obj, characterOffset):
        contents = self.getLineAtOffset(obj, characterOffset)

        if not len(contents):
            return

        for content in contents:
            [obj, startOffset, endOffset] = content
            if not obj:
                continue

            if obj.text:
                string = self.getText(obj, startOffset, endOffset)
            else:
                string = obj.name

            # Debug code.
            #
            #if obj.role == rolenames.ROLE_TABLE_CELL:
            #    [row, col] = self.getCellCoordinates(obj)
            #    [rowHeader, colHeader] = self.getCellHeaders(obj)
            #    captionObj = self.getTableCaption(obj.parent)
            #    if captionObj:
            #        caption = util.getDisplayedText(captionObj)
            #    else:
            #        caption = ""
            #    print "FOO", string, caption, row, col, rowHeader, colHeader

            self.presentString(obj, string, True)

    def getContents(self):
        """Trivial debug utility to stringify the document contents
        showing on the screen."""

        contents = ""
        lastObj = None
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
            [obj, characterOffset] = self.getNextCaretInOrder(obj,
                                                              characterOffset)
        if lastObj and lastObj.role == rolenames.ROLE_LINK:
            contents += ">"
        return contents

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

    def dumpContent(self, inputEvent, contents=None):
        """Dumps the document frame content to stdout.

        Arguments:
        -inputEvent: the input event that caused this to be called
        -contents: an ordered list of [obj, startOffset, endOffset] tuples
        """
        if not contents:
            contents = self.getLinearizedContents()
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

    def setCaretPosition(self, obj, characterOffset):
        """Sets the caret position to the given character offset in the
        given object.
        """

        caretContext = self.getCaretContext()
        if caretContext == [obj, characterOffset]:
            return

        self.caretContext = [obj, characterOffset]

        # We'd like the thing to have focus if it can take focus.
        #
        focusGrabbed = obj.component.grabFocus()
        if not focusGrabbed:
            print "FOCUS NOT GRABBED", obj.role, characterOffset

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
            else:
                caretSet = False
            if not caretSet:
                print "CARET NOT SET", obj.role, characterOffset

    def goNextCharacter(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the document window.
        """

        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.getNextCaretInOrder(obj,
                                                              characterOffset)
            if obj and obj.state.count(atspi.Accessibility.STATE_SHOWING):
                self.caretContext = [obj, characterOffset]
                break

        if obj:
            self.setCaretPosition(obj, characterOffset)
        else:
            del self.caretContext

        self.presentCharacterAtOffset(obj, characterOffset)

    def goPreviousCharacter(self, inputEvent):
        """Positions the caret offset to the previous character or object
        in the document window.
        """
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.getPreviousCaretInOrder(
                obj, characterOffset)
            if obj and obj.state.count(atspi.Accessibility.STATE_SHOWING):
                self.caretContext = [obj, characterOffset]
                break

        if obj:
            self.setCaretPosition(obj, characterOffset)
        else:
            del self.caretContext

        self.presentCharacterAtOffset(obj, characterOffset)

    def goPreviousWord(self, inputEvent):
        """Positions the caret offset to beginning of the previous
        word or object in the document window.
        """

        # Find the beginning of the current word
        #
        [obj, characterOffset] = self.getCaretContext()
        contents = self.getWordAtOffset(obj, characterOffset)
        [obj, startOffset, endOffset] = contents[0]

        # Now go to the beginning of the previous word
        #
        [obj, characterOffset] = self.getPreviousCaretInOrder(obj, startOffset)
        contents = self.getWordAtOffset(obj, characterOffset)
        [obj, startOffset, endOffset] = contents[0]

        self.setCaretPosition(obj,  startOffset)
        self.presentWordAtOffset(obj, startOffset)

    def goNextWord(self, inputEvent):
        """Positions the caret offset to the end of next word or object
        in the document window.
        """

        # Find the beginning of the current word
        #
        [obj, characterOffset] = self.getCaretContext()
        contents = self.getWordAtOffset(obj, characterOffset)
        [obj, startOffset, endOffset] = contents[0]

        # Now go to the beginning of the next word.
        #
        [obj, characterOffset] = self.getNextCaretInOrder(obj, endOffset - 1)
        contents = self.getWordAtOffset(obj, characterOffset)
        [obj, startOffset, endOffset] = contents[0]

        # [[[TODO: WDW - to be more like gedit, we should position the
        # caret just after the last character of the word.]]]
        #
        self.setCaretPosition(obj,  startOffset)
        self.presentWordAtOffset(obj, startOffset)

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
                  self.getPreviousCaretInOrder(obj, characterOffset)

        #print "GPL ENDED UP AT", lastObj.role, lineExtents
        self.setCaretPosition(lastObj, lastCharacterOffset)
        self.presentLineAtOffset(lastObj, lastCharacterOffset)

        # Debug...
        #
        contents = self.getLineAtOffset(lastObj, lastCharacterOffset)
        self.dumpContent(inputEvent, contents)

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
                     and (extents[0] >= characterExtents[0]):
                    break
                else:
                    lineExtents = self.getBoundary(extents, lineExtents)

                [lastObj, lastCharacterOffset] = [obj, characterOffset]

            [obj, characterOffset] = \
                  self.getNextCaretInOrder(obj, characterOffset)

        #print "GNL ENDED UP AT", lastObj.role, lineExtents
        self.setCaretPosition(lastObj, lastCharacterOffset)
        self.presentLineAtOffset(lastObj, lastCharacterOffset)

        # Debug...
        #
        contents = self.getLineAtOffset(lastObj, lastCharacterOffset)
        self.dumpContent(inputEvent, contents)

    def getPreviousRole(self, role):
        """Positions the caret offset at the beginnig of the next object
        of the given role.
        """
        [currentObj, characterOffset] = self.getCaretContext()

        obj = currentObj
        while obj:
            [obj, characterOffset] = self.getPreviousCaretInOrder(
                obj, characterOffset)
            if obj and (obj != currentObj) and (obj.role == role):
                return [obj, characterOffset]

        return [None, -1]

    def getNextRole(self, role):
        """Positions the caret offset at the beginnig of the next object
        of the given role.
        """
        [currentObj, characterOffset] = self.getCaretContext()

        obj = currentObj
        while obj:
            [obj, characterOffset] = self.getNextCaretInOrder(
                obj, characterOffset)
            if obj and (obj != currentObj) and (obj.role == role):
                return [obj, characterOffset]

        return [None, -1]

    def goPreviousHeading(self, inputEvent):
        [obj, characterOffset] = self.getPreviousRole(rolenames.ROLE_HEADING)
        if obj:
            [obj, characterOffset] = self.getFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLineAtOffset(obj, characterOffset)
        else:
            speech.speak("No more headings.")

    def goNextHeading(self, inputEvent):
        [obj, characterOffset] = self.getNextRole(rolenames.ROLE_HEADING)
        if obj:
            [obj, characterOffset] = self.getFirstCaretContext(obj, 0)
            self.setCaretPosition(obj, characterOffset)
            self.presentLineAtOffset(obj, characterOffset)
        else:
            speech.speak("No more headings.")
