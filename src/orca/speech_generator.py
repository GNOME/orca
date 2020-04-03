# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Utilities for obtaining speech utterances for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import urllib.parse, urllib.request, urllib.error, urllib.parse

from . import chnames
from . import debug
from . import generator
from . import messages
from . import object_properties
from . import settings
from . import settings_manager
from . import text_attribute_names
from . import acss

class Pause:
    """A dummy class to indicate we want to insert a pause into an
    utterance."""
    def __init__(self):
        pass

PAUSE = [Pause()]

class LineBreak:
    """A dummy class to indicate we want to break an utterance into
    separate calls to speak."""
    def __init__(self):
        pass

LINE_BREAK = [LineBreak()]

# [[[WDW - general note -- for all the _generate* methods, it would be great if
# we could return an empty array if we can determine the method does not
# apply to the object.  This would allow us to reduce the number of strings
# needed in formatting.py.]]]

# The prefix to use for the individual generator methods
#
METHOD_PREFIX = "_generate"

DEFAULT        = "default"
UPPERCASE      = "uppercase"
HYPERLINK      = "hyperlink"
SYSTEM         = "system"
STATE          = "state" # Candidate for sound
VALUE          = "value" # Candidate for sound

voiceType = {
    DEFAULT: settings.DEFAULT_VOICE,
    UPPERCASE: settings.UPPERCASE_VOICE,
    HYPERLINK: settings.HYPERLINK_VOICE,
    SYSTEM: settings.SYSTEM_VOICE,
    STATE: settings.SYSTEM_VOICE, # Users may prefer DEFAULT_VOICE here
    VALUE: settings.SYSTEM_VOICE, # Users may prefer DEFAULT_VOICE here
}

_settingsManager = settings_manager.getManager()

class SpeechGenerator(generator.Generator):
    """Takes accessible objects and produces a string to speak for
    those objects.  See the generateSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speechGenerators instance field as they see fit."""

    # pylint: disable-msg=W0142

    def __init__(self, script):
        generator.Generator.__init__(self, script, "speech")

    def _getACSS(self, obj, string):
        if obj.getRole() == pyatspi.ROLE_LINK:
            acss = self.voice(HYPERLINK)
        elif isinstance(string, str) \
            and string.isupper() \
            and string.strip().isalpha():
            acss = self.voice(UPPERCASE)
        else:
            acss = self.voice(DEFAULT)

        return acss

    def _addGlobals(self, globalsDict):
        """Other things to make available from the formatting string.
        """
        generator.Generator._addGlobals(self, globalsDict)
        globalsDict['voice'] = self.voice

    def generateSpeech(self, obj, **args):
        return self.generate(obj, **args)

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _generateName(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the name of the object.  If the object is directly
        displaying any text, that text will be treated as the name.
        Otherwise, the accessible name of the object will be used.  If
        there is no accessible name, then the description of the
        object will be used.  This method will return an empty array
        if nothing can be found.  [[[WDW - I wonder if we should just
        have _generateName, _generateDescription,
        _generateDisplayedText, etc., that don't do any fallback.
        Then, we can allow the formatting to do the fallback (e.g.,
        'displayedText or name or description'). [[[JD to WDW - I
        needed a _generateDescription for whereAmI. :-) See below.
        """

        try:
            role = args.get('role', obj.getRole())
        except (LookupError, RuntimeError):
            debug.println(debug.LEVEL_FINE, "Error getting role for: %s" % obj)
            role = None

        if role == pyatspi.ROLE_LAYERED_PANE:
            if _settingsManager.getSetting('onlySpeakDisplayedText'):
                return []
            else:
                acss = self.voice(SYSTEM)
        else:
            acss = self.voice(DEFAULT)
        result = generator.Generator._generateName(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateLabel(self, obj, **args):
        """Returns the label for an object as an array of strings for use by
        speech and braille.  The label is determined by the displayedLabel
        method of the script utility, and an empty array will be returned if
        no label can be found.
        """
        acss = self.voice(DEFAULT)
        result = generator.Generator._generateLabel(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateLabelOrName(self, obj, **args):
        """Returns the label as an array of strings for speech and braille.
        If the label cannot be found, the name will be used instead.
        If the name cannot be found, an empty array will be returned.
        """
        result = []
        acss = self.voice(DEFAULT)
        result.extend(self._generateLabel(obj, **args))
        if not result:
            try:
                name = obj.name
            except:
                msg = 'ERROR: Could not get name for %s' % obj
                debug.println(debug.LEVEL_INFO, msg)
                return result
            if name:
                result.append(name)
                result.extend(acss)
        if not result and obj.parent and obj.parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            result = self._generateLabelOrName(obj.parent, **args)

        return result

    def _generatePlaceholderText(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the 'placeholder' text. This is typically text that
        serves as a functional label and is found in a text widget until
        that widget is given focus at which point the text is removed,
        the assumption being that the user was able to see the text prior
        to giving the widget focus.
        """
        acss = self.voice(DEFAULT)
        result = generator.Generator._generatePlaceholderText(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings fo use by speech and braille that
        represent the description of the object, if that description
        is different from that of the name and label.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not _settingsManager.getSetting('speakDescription'):
            return []

        if args.get('inMouseReview') and not _settingsManager.getSetting('presentToolTips'):
            return []

        priorObj = args.get('priorObj')
        if priorObj and priorObj.getRole() == pyatspi.ROLE_TOOL_TIP:
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateDescription(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateImageDescription(self, obj, **args ):
        """Returns an array of strings for use by speech and braille that
        represent the description of the image on the object."""

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not _settingsManager.getSetting('speakDescription'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateImageDescription(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateReadOnly(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the read only state of this object, but only if it
        is read only (i.e., it is a text area that cannot be edited).
        """
        acss = self.voice(SYSTEM)
        result = generator.Generator._generateReadOnly(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateHasPopup(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or _settingsManager.getSetting('speechVerbosityLevel') \
               == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateHasPopup(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateClickable(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or _settingsManager.getSetting('speechVerbosityLevel') \
               == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateClickable(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateHasLongDesc(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateHasLongDesc(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateHasDetails(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateHasDetails(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateDetailsFor(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateDetailsFor(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateAllDetails(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateAllDetails(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateDeletionStart(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        startOffset = args.get('startOffset', 0)
        if startOffset != 0:
            return []

        result = []
        if self._script.utilities.isFirstItemInInlineContentSuggestion(obj):
            result.extend([object_properties.ROLE_CONTENT_SUGGESTION])
            result.extend(self.voice(SYSTEM))
            result.extend(self._generatePause(obj, **args))

        result.extend([messages.CONTENT_DELETION_START])
        result.extend(self.voice(SYSTEM))
        return result

    def _generateDeletionEnd(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        endOffset = args.get('endOffset')
        if endOffset is not None:
            text = self._script.utilities.queryNonEmptyText(obj)
            if text  and text.characterCount != endOffset:
                return []

        result = [messages.CONTENT_DELETION_END]
        result.extend(self.voice(SYSTEM))

        if self._script.utilities.isLastItemInInlineContentSuggestion(obj):
            result.extend(self._generatePause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM))

            container = pyatspi.findAncestor(obj, self._script.utilities.hasDetails)
            if self._script.utilities.isContentSuggestion(container):
                result.extend(self._generatePause(obj, **args))
                result.extend(self._generateHasDetails(container, mode=args.get('mode')))

        return result

    def _generateInsertionStart(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        startOffset = args.get('startOffset', 0)
        if startOffset != 0:
            return []

        result = []
        if self._script.utilities.isFirstItemInInlineContentSuggestion(obj):
            result.extend([object_properties.ROLE_CONTENT_SUGGESTION])
            result.extend(self.voice(SYSTEM))
            result.extend(self._generatePause(obj, **args))

        result.extend([messages.CONTENT_INSERTION_START])
        result.extend(self.voice(SYSTEM))
        return result

    def _generateInsertionEnd(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        endOffset = args.get('endOffset')
        if endOffset is not None:
            text = self._script.utilities.queryNonEmptyText(obj)
            if text and text.characterCount != endOffset:
                return []

        result = [messages.CONTENT_INSERTION_END]
        result.extend(self.voice(SYSTEM))

        if self._script.utilities.isLastItemInInlineContentSuggestion(obj):
            result.extend(self._generatePause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM))

            container = pyatspi.findAncestor(obj, self._script.utilities.hasDetails)
            if self._script.utilities.isContentSuggestion(container):
                result.extend(self._generatePause(obj, **args))
                result.extend(self._generateHasDetails(container, mode=args.get('mode')))

        return result

    def _generateMarkStart(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        startOffset = args.get('startOffset', 0)
        if startOffset != 0:
            return []

        result = []
        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            result.append(roledescription)
            result.extend(self.voice(SYSTEM))
            result.extend(self._generatePause(obj, **args))

        result.append(messages.CONTENT_MARK_START)
        result.extend(self.voice(SYSTEM))
        return result

    def _generateMarkEnd(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        endOffset = args.get('endOffset')
        if endOffset is not None:
            text = self._script.utilities.queryNonEmptyText(obj)
            if text and text.characterCount != endOffset:
                return []

        result = [messages.CONTENT_MARK_END]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateSuggestionStart(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = [messages.CONTENT_SUGGESTION_START]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateAvailability(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateAvailability(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateInvalid(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateInvalid(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateRequired(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateRequired(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateTable(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if args.get("leaving"):
            return[]

        if self._script.utilities.isTextDocumentTable(obj):
            role = args.get('role', obj.getRole())
            enabled, disabled = self._getEnabledAndDisabledContextRoles()
            if role in disabled:
                return []
        elif _settingsManager.getSetting('speechVerbosityLevel') == \
           settings.VERBOSITY_LEVEL_BRIEF:
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateTable(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateTextRole(self, obj, **args):
        """A convenience method to prevent the pyatspi.ROLE_PARAGRAPH role
        from being spoken. In the case of a pyatspi.ROLE_PARAGRAPH
        role, an empty array will be returned. In all other cases, the
        role name will be returned as an array of strings (and
        possibly voice and audio specifications).  Note that a 'role'
        attribute in args will override the accessible role of the
        obj. [[[WDW - I wonder if this should be moved to
        _generateRoleName.  Or, maybe make a 'do not speak roles' attribute
        of a speech generator that we can update and the user can
        override.]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        role = args.get('role', obj.getRole())
        if role != pyatspi.ROLE_PARAGRAPH:
            result.extend(self._generateRoleName(obj, **args))
        return result

    def _generateRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings (and
        possibly voice and audio specifications), with the exception
        that the pyatspi.ROLE_UNKNOWN role will yield an empty array.
        Note that a 'role' attribute in args will override the
        accessible role of the obj.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if self._script.utilities.isStatusBarNotification(obj):
            return []

        if self._script.utilities.isDesktop(obj):
            return []

        result = []
        acss = self.voice(SYSTEM)
        role = args.get('role', obj.getRole())

        doNotPresent = [pyatspi.ROLE_UNKNOWN,
                        pyatspi.ROLE_REDUNDANT_OBJECT,
                        pyatspi.ROLE_FILLER,
                        pyatspi.ROLE_EXTENDED]

        try:
            parentRole = obj.parent.getRole()
        except:
            parentRole = None

        if role == pyatspi.ROLE_MENU and parentRole == pyatspi.ROLE_COMBO_BOX:
            return self._generateRoleName(obj.parent)

        if role == pyatspi.ROLE_ENTRY \
           and obj.getState().contains(pyatspi.STATE_SUPPORTS_AUTOCOMPLETION):
            result.append(self.getLocalizedRoleName(obj, role=pyatspi.ROLE_AUTOCOMPLETE))
            result.extend(acss)

        if role == pyatspi.ROLE_PANEL and obj.getState().contains(pyatspi.STATE_SELECTED):
            return []

        # egg-list-box, e.g. privacy panel in gnome-control-center
        if parentRole == pyatspi.ROLE_LIST_BOX:
            doNotPresent.append(obj.getRole())

        if _settingsManager.getSetting('speechVerbosityLevel') \
                == settings.VERBOSITY_LEVEL_BRIEF:
            doNotPresent.extend([pyatspi.ROLE_ICON, pyatspi.ROLE_CANVAS])

        if role == pyatspi.ROLE_HEADING:
            level = self._script.utilities.headingLevel(obj)
            if level:
                result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                    'role': self.getLocalizedRoleName(obj, **args),
                    'level': level})
                result.extend(acss)

        if role not in doNotPresent and not result:
            result.append(self.getLocalizedRoleName(obj, **args))
            result.extend(acss)
        return result

    def getRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings (and
        possibly voice and audio specifications), with the exception
        that the pyatspi.ROLE_UNKNOWN role will yield an empty array.
        Note that a 'role' attribute in args will override the
        accessible role of the obj.  This is provided mostly as a
        method for scripts to call.
        """
        generated = self._generateRoleName(obj, **args)
        if generated:
            return generated[0]

        return ""

    def getName(self, obj, **args):
        generated = self._generateName(obj, **args)
        if generated:
            return generated[0]

        return ""

    def getLocalizedRoleName(self, obj, **args):
        """Returns the localized name of the given Accessible object; the name
        is suitable to be spoken.

        Arguments:
        - obj: an Accessible object
        """

        if self._script.utilities.isEditableComboBox(obj) \
           or self._script.utilities.isEditableDescendantOfComboBox(obj):
            return object_properties.ROLE_EDITABLE_COMBO_BOX

        role = args.get('role', obj.getRole())
        state = obj.getState()
        if role == pyatspi.ROLE_LINK and state.contains(pyatspi.STATE_VISITED):
            return object_properties.ROLE_VISITED_LINK

        return super().getLocalizedRoleName(obj, **args)

    def _generateUnrelatedLabels(self, obj, **args):
        """Returns, as an array of strings (and possibly voice
        specifications), all the labels which are underneath the obj's
        hierarchy and which are not in a label for or labelled by
        relation.
        """
        result = []
        acss = self.voice(DEFAULT)
        visibleOnly = not self._script.utilities.isStatusBarNotification(obj)

        minimumWords = 1
        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_PANEL]:
            minimumWords = 3

        labels = self._script.utilities.unrelatedLabels(obj, visibleOnly, minimumWords)
        for label in labels:
            name = self._generateName(label, **args)
            if name and len(name[0]) == 1:
                charname = chnames.getCharacterName(name[0])
                if charname:
                    name[0] = charname
            result.extend(name)
        if result:
            result.extend(acss)
        return result

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generateCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = generator.Generator._generateCheckedState(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateExpandableState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the expanded/collapsed state of an object, such as a
        tree node. If the object is not expandable, an empty array
        will be returned.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = generator.Generator._generateExpandableState(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateCheckedStateIfCheckable(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = super()._generateCheckedStateIfCheckable(obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateMenuItemCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the menu item, only if it is
        checked. Otherwise, and empty array will be returned.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = generator.Generator.\
            _generateMenuItemCheckedState(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateMultiselectableState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the multiselectable state of
        the object.  This is typically for list boxes. If the object
        is not multiselectable, an empty array will be returned.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = super()._generateMultiselectableState(obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateRadioState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = generator.Generator._generateRadioState(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateSwitchState(self, obj, **args):
        """Returns an array of strings indicating the on/off state of obj."""
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = generator.Generator._generateSwitchState(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    def _generateToggleState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(STATE)
        result = generator.Generator._generateToggleState(self, obj, **args)
        if result:
            result.extend(acss)
        return result

    #####################################################################
    #                                                                   #
    # Link information                                                  #
    #                                                                   #
    #####################################################################

    def generateLinkInfo(self, obj, **args):
        result = self._generateLinkInfo(obj, **args)
        result.extend(self._generatePause(obj, **args))
        result.append(self._generateSiteDescription(obj, **args))
        result.extend(self._generatePause(obj, **args))
        result.append(self._generateFileSize(obj, **args))
        return result

    def _generateLinkInfo(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the protocol of the URI of
        the link associated with obj.
        """
        result = []
        acss = self.voice(HYPERLINK)
        # Get the URI for the link of interest and parse it. The parsed
        # URI is returned as a tuple containing six components:
        # scheme://netloc/path;parameters?query#fragment.
        #
        link_uri = self._script.utilities.uri(obj)
        if not link_uri:
            # [[[TODO - JD: For some reason, this is failing for certain
            # links. The current whereAmI code says, "It might be an anchor.
            # Try to speak the text." and passes things off to whereAmI's
            # _speakText method. That won't work in the new world order.
            # Therefore, for now, I will hack in some code to do that
            # work here so that the before and after end results match.]]]
            #
            result.extend(self._generateLabel(obj))
            result.extend(self._generateRoleName(obj))
            result.append(self._script.utilities.displayedText(obj))
        else:
            link_uri_info = urllib.parse.urlparse(link_uri)
            if link_uri_info[0] in ["ftp", "ftps", "file"]:
                fileName = link_uri_info[2].split('/')
                result.append(messages.LINK_TO_FILE \
                              % {"uri" : link_uri_info[0],
                                 "file" : fileName[-1]})
            else:
                linkOutput = messages.LINK_WITH_PROTOCOL % link_uri_info[0]
                text = self._script.utilities.displayedText(obj)
                try:
                    isVisited = obj.getState().contains(pyatspi.STATE_VISITED)
                except:
                    isVisited = False
                if not isVisited:
                    linkOutput = messages.LINK_WITH_PROTOCOL % link_uri_info[0]
                else:
                    linkOutput = messages.LINK_WITH_PROTOCOL_VISITED % link_uri_info[0]
                if not text:
                    # If there's no text for the link, expose part of the
                    # URI to the user.
                    #
                    text = self._script.utilities.linkBasename(obj)
                if text:
                    linkOutput += " " + text
                result.append(linkOutput)
                if obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                    result.extend(self._generateRoleName(obj[0]))
        if result:
            result.extend(acss)
        return result

    def _generateSiteDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that describe the site (same or different)
        pointed to by the URI of the link associated with obj.
        """
        result = []
        acss = self.voice(HYPERLINK)
        link_uri = self._script.utilities.uri(obj)
        if link_uri:
            link_uri_info = urllib.parse.urlparse(link_uri)
        else:
            return result
        doc_uri = self._script.utilities.documentFrameURI()
        if doc_uri:
            doc_uri_info = urllib.parse.urlparse(doc_uri)
            if link_uri_info[1] == doc_uri_info[1]:
                if link_uri_info[2] == doc_uri_info[2]:
                    result.append(messages.LINK_SAME_PAGE)
                else:
                    result.append(messages.LINK_SAME_SITE)
            else:
                # check for different machine name on same site
                #
                linkdomain = link_uri_info[1].split('.')
                docdomain = doc_uri_info[1].split('.')
                if len(linkdomain) > 1 and len(docdomain) > 1  \
                    and linkdomain[-1] == docdomain[-1]  \
                    and linkdomain[-2] == docdomain[-2]:
                    result.append(messages.LINK_SAME_SITE)
                else:
                    result.append(messages.LINK_DIFFERENT_SITE)

        if result:
            result.extend(acss)
        return result

    def _generateFileSize(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the size (Content-length) of
        the file pointed to by the URI of the link associated with
        obj.
        """
        result = []
        acss = self.voice(HYPERLINK)
        sizeString = ""
        uri = self._script.utilities.uri(obj)
        if not uri:
            return result
        try:
            x = urllib.request.urlopen(uri)
            try:
                sizeString = x.info()['Content-length']
            except KeyError:
                pass
        except (ValueError, urllib.error.URLError, OSError):
            pass
        if sizeString:
            size = int(sizeString)
            if size < 10000:
                result.append(messages.fileSizeBytes(size))
            elif size < 1000000:
                result.append(messages.FILE_SIZE_KB % (float(size) * .001))
            elif size >= 1000000:
                result.append(messages.FILE_SIZE_MB % (float(size) * .000001))
        if result:
            result.extend(acss)
        return result

    #####################################################################
    #                                                                   #
    # Image information                                                 #
    #                                                                   #
    #####################################################################

    def _generateImage(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the image on the the object, if
        it exists.  Otherwise, an empty array is returned.
        """
        result = []
        acss = self.voice(DEFAULT)
        try:
            image = obj.queryImage()
        except:
            pass
        else:
            args['role'] = pyatspi.ROLE_IMAGE
            result.extend(self.generate(obj, **args))
            result.extend(acss)
        return result

    #####################################################################
    #                                                                   #
    # Table interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateColumnHeader(self, obj, **args):
        if self._script.inSayAll():
            return []

        result = super()._generateColumnHeader(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT))

        return result

    def _generateRowHeader(self, obj, **args):
        if self._script.inSayAll():
            return []

        result = super()._generateRowHeader(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT))

        return result

    def _generateNewRowHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the row header for an object
        that is in a table, if it exists and if it is different from
        the previous row header.  Otherwise, an empty array is
        returned.  The previous row header is determined by looking at
        the row header for the 'priorObj' attribute of the args
        dictionary.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """

        if not self._script.utilities.cellRowChanged(obj):
            return []

        args['newOnly'] = True
        return self._generateRowHeader(obj, **args)

    def _generateNewColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists and if it is different from
        the previous column header.  Otherwise, an empty array is
        returned.  The previous column header is determined by looking
        at the column header for the 'priorObj' attribute of the args
        dictionary.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """

        if not self._script.utilities.cellColumnChanged(obj):
            return []

        if args.get('readingRow'):
            return []

        args['newOnly'] = True
        return self._generateColumnHeader(obj, **args)

    def _generateRealTableCell(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to complexity in
        the code.  This method is used to return an array of strings
        (and possibly voice and audio specifications) for a single table
        cell itself.  The string, 'blank', is added for empty cells.
        """
        result = []
        acss = self.voice(DEFAULT)
        oldRole = self._overrideRole('REAL_ROLE_TABLE_CELL', args)
        result.extend(self.generate(obj, **args))
        self._restoreRole(oldRole, args)
        if not (result and result[0]) \
           and _settingsManager.getSetting('speakBlankLines') \
           and not args.get('readingRow', False):
            result.append(messages.BLANK)
            if result:
                result.extend(acss)

        return result

    def _generateUnselectedCell(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) if this is an icon within an layered pane or a
        table cell within a table or a tree table and the item is
        focused but not selected.  Otherwise, an empty array is
        returned.  [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if args.get('inMouseReview'):
            return []

        if not obj:
            return []

        if not (obj.parent and 'Selection' in pyatspi.listInterfaces(obj.parent)):
            return []

        state = obj.getState()
        if state.contains(pyatspi.STATE_SELECTED):
            return []

        if obj.getRole() == pyatspi.ROLE_TEXT:
            return []

        parentRole = obj.parent.getRole()
        if parentRole in [pyatspi.ROLE_TREE_TABLE, pyatspi.ROLE_TABLE]:
            lastKey, mods = self._script.utilities.lastKeyAndModifiers()
            if lastKey in ["Left", "Right"]:
                return []
            if self._script.utilities.isLayoutOnly(obj.parent):
                return []
        elif parentRole == pyatspi.ROLE_LAYERED_PANE:
            if obj in self._script.utilities.selectedChildren(obj.parent):
                return []
        else:
            return []

        result = [object_properties.STATE_UNSELECTED_TABLE_CELL]
        result.extend(self.voice(STATE))

        return result

    def _generateColumn(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the column number of a cell.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        col = -1
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent
        try:
            table = parent.queryTable()
        except:
            if args.get('guessCoordinates', False):
                col = self._script.pointOfReference.get('lastColumn', -1)
        else:
            index = self._script.utilities.cellIndex(obj)
            col = table.getColumnAtIndex(index)
        if col >= 0:
            result.append(messages.TABLE_COLUMN % (col + 1))
        if result:
            result.extend(acss)
        return result

    def _generateRow(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the row number of a cell.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        row = -1
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent
        try:
            table = parent.queryTable()
        except:
            if args.get('guessCoordinates', False):
                row = self._script.pointOfReference.get('lastRow', -1)
        else:
            index = self._script.utilities.cellIndex(obj)
            row = table.getRowAtIndex(index)
        if row >= 0:
            result.append(messages.TABLE_ROW % (row + 1))
        if result:
            result.extend(acss)
        return result

    def _generateColumnAndRow(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the position of the cell in terms
        of its column number, the total number of columns, its row,
        and the total number of rows.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent
        try:
            table = parent.queryTable()
        except:
            table = None
        else:
            index = self._script.utilities.cellIndex(obj)
            col = table.getColumnAtIndex(index)
            row = table.getRowAtIndex(index)
            result.append(messages.TABLE_COLUMN_DETAILED \
                          % {"index" : (col + 1),
                             "total" : table.nColumns})
            result.append(messages.TABLE_ROW_DETAILED \
                          % {"index" : (row + 1),
                             "total" : table.nRows})
        if result:
            result.extend(acss)
        return result

    def _generateEndOfTableIndicator(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) indicating that this cell is the last cell
        in the table.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if _settingsManager.getSetting('speechVerbosityLevel') \
           != settings.VERBOSITY_LEVEL_VERBOSE:
            return []

        if self._script.utilities.isLastCell(obj):
            result = [messages.TABLE_END]
            result.extend(self.voice(SYSTEM))
            return result

        return []

    #####################################################################
    #                                                                   #
    # Text interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateCurrentLineText(self, obj, **args):
        """Returns an array of strings for use by speech and braille
        that represents the current line of text, if
        this is a text object.  [[[WDW - consider returning an empty
        array if this is not a text object.]]]
        """

        if args.get('inMouseReview') and obj.getState().contains(pyatspi.STATE_EDITABLE):
            return []

        result = self._generateSubstring(obj, **args)
        if result and result[0]:
            return result

        acss = self.voice(DEFAULT)
        result = generator.Generator._generateCurrentLineText(self, obj, **args)
        if not (result and result[0]):
            return []

        if result == ['\n'] and _settingsManager.getSetting('speakBlankLines') \
           and not self._script.inSayAll() and args.get('total', 1) == 1:
            result = [messages.BLANK]

        result.extend(acss)
        return result

    def _generateDisplayedText(self, obj, **args):
        result = self._generateSubstring(obj, **args)
        if result and result[0]:
            return result

        acss = self.voice(DEFAULT)
        result = generator.Generator._generateDisplayedText(self, obj, **args)
        if not (result and result[0]):
            return []

        string = result[0].strip()
        if len(string) == 1 and self._script.utilities.isMath(obj):
            charname = chnames.getCharacterName(string, preferMath=True)
            if charname != string:
                result[0] = charname
            result.extend(acss)

        return result

    def _getCharacterAttributes(self,
                                obj,
                                text,
                                textOffset,
                                lineIndex,
                                keys=["style", "weight", "underline"]):
        """Helper function that returns a string containing the
        given attributes from keys for the given character.
        """
        attribStr = ""

        defaultAttributes = text.getDefaultAttributes()
        keyList, attributesDictionary = \
            self._script.utilities.stringToKeysAndDict(defaultAttributes)

        charAttributes = text.getAttributes(textOffset)
        if charAttributes[0]:
            keyList, charDict = \
                self._script.utilities.stringToKeysAndDict(charAttributes[0])
            for key in keyList:
                attributesDictionary[key] = charDict[key]

        if attributesDictionary:
            for key in keys:
                localizedKey = text_attribute_names.getTextAttributeName(
                    key, self._script)
                if key in attributesDictionary:
                    attribute = attributesDictionary[key]
                    localizedValue = text_attribute_names.getTextAttributeName(
                        attribute, self._script)
                    if attribute:
                        # If it's the 'weight' attribute and greater than 400,
                        # just speak it as bold, otherwise speak the weight.
                        #
                        if key == "weight":
                            if int(attribute) > 400:
                                attribStr += " %s" % messages.BOLD
                        elif key == "underline":
                            if attribute != "none":
                                attribStr += " %s" % localizedKey
                        elif key == "style":
                            if attribute != "normal":
                                attribStr += " %s" % localizedValue
                        else:
                            attribStr += " "
                            attribStr += (localizedKey + " " + localizedValue)

            # Also check to see if this is a hypertext link.
            #
            if self._script.utilities.linkIndex(obj, textOffset) >= 0:
                attribStr += " %s" % messages.LINK

        return attribStr

    def _getTextInformation(self, obj):
        """Returns [textContents, startOffset, endOffset, selected] as
        follows:

        A. if no text on the current line is selected, the current line
        B. if text is selected, the selected text
        C. if the current line is blank/empty, 'blank'

        Also sets up a 'textInformation' attribute in
        self._script.generatorCache to prevent computing this
        information repeatedly while processing a single event.
        """

        try:
            return self._script.generatorCache['textInformation']
        except:
            pass

        textObj = obj.queryText()
        caretOffset = textObj.caretOffset

        textContents, startOffset, endOffset = self._script.utilities.allSelectedText(obj)
        selected = textContents != ""

        if not selected:
            # Get the line containing the caret
            #
            [line, startOffset, endOffset] = textObj.getTextAtOffset(
                textObj.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            if len(line):
                line = self._script.utilities.adjustForRepeats(line)
                textContents = line
            else:
                char = textObj.getTextAtOffset(caretOffset,
                    pyatspi.TEXT_BOUNDARY_CHAR)
                if char[0] == "\n" and startOffset == caretOffset:
                    textContents = char[0]

        self._script.generatorCache['textInformation'] = \
            [textContents, startOffset, endOffset, selected]

        return self._script.generatorCache['textInformation']

    def _generateTextContent(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the text content.  This requires
        _generateTextInformation to have been called prior to this method.
        """

        result = self._generateSubstring(obj, **args)
        if result:
            return result

        try:
            text = obj.queryText()
        except NotImplementedError:
            return []

        result = []
        acss = self.voice(DEFAULT)
        [line, startOffset, endOffset, selected] = \
            self._getTextInformation(obj)

        # The empty string seems to be messing with using 'or' in
        # formatting strings.
        #
        if line:
            result.append(line)
            result.extend(acss)

        return result

    def _generateTextContentWithAttributes(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the text content, obtained from the
        'textInformation' value, with character attribute information
        mixed in.  This requires _generateTextInformation to have been
        called prior to this method.
        """

        try:
            text = obj.queryText()
        except NotImplementedError:
            return []

        acss = self.voice(DEFAULT)
        [line, startOffset, endOffset, selected] = \
            self._getTextInformation(obj)

        newLine = ""
        lastAttribs = None
        textOffset = startOffset
        for i in range(0, len(line)):
            attribs = self._getCharacterAttributes(obj, text, textOffset, i)
            if attribs and attribs != lastAttribs:
                if newLine:
                    newLine += " ; "
                newLine += attribs
                newLine += " "
            lastAttribs = attribs
            newLine += line[i]
            textOffset += 1

        attribs = self._getCharacterAttributes(obj,
                                               text,
                                               startOffset,
                                               0,
                                               ["paragraph-style"])

        if attribs:
            if newLine:
                newLine += " ; "
            newLine += attribs

        result = [newLine]
        result.extend(acss)
        return result

    def _generateAnyTextSelection(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if any of the text for the entire
        object is selected. [[[WDW - I wonder if this string should be
        moved to settings.py.]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        try:
            text = obj.queryText()
        except NotImplementedError:
            return []

        result = []
        acss = self.voice(SYSTEM)

        [line, startOffset, endOffset, selected] = \
            self._getTextInformation(obj)

        if selected:
            result.append(messages.TEXT_SELECTED)
            result.extend(acss)
        return result

    def _generateAllTextSelection(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if all the text for the entire
        object is selected. [[[WDW - I wonder if this string should be
        moved to settings.py.]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        try:
            textObj = obj.queryText()
        except:
            pass
        else:
            noOfSelections = textObj.getNSelections()
            if noOfSelections == 1:
                [string, startOffset, endOffset] = \
                   textObj.getTextAtOffset(0, pyatspi.TEXT_BOUNDARY_LINE_START)
                if startOffset == 0 and endOffset == len(string):
                    result = [messages.TEXT_SELECTED]
                    result.extend(acss)
        return result

    def _generateSubstring(self, obj, **args):
        result = super()._generateSubstring(obj, **args)
        if not (result and result[0]):
            return []

        if not obj.getState().contains(pyatspi.STATE_EDITABLE):
            result[0] = result[0].strip()

        result.extend(self._getACSS(obj, result[0]))
        if result[0] in ['\n', ''] and _settingsManager.getSetting('speakBlankLines') \
           and not self._script.inSayAll() and args.get('total', 1) == 1:
            result[0] = messages.BLANK

        return result

    def _generateTextIndentation(self, obj, **args):
        """Speaks a summary of the number of spaces and/or tabs at the
        beginning of the given line.

        Arguments:
        - obj: the text object.
        """

        if not _settingsManager.getSetting('enableSpeechIndentation'):
            return []

        line, caretOffset, startOffset = self._script.getTextLineAtCaret(obj)
        description = self._script.utilities.indentationDescription(line)
        if not description:
            return []

        result = [description]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateNestingLevel(self, obj, **args):
        result = super()._generateNestingLevel(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM))

        return result

    #####################################################################
    #                                                                   #
    # Tree interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateNewNodeLevel(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the tree node level of the
        object, or an empty array if the object is not a tree node or
        if the node level is not different from the 'priorObj'
        'priorObj' attribute of the args dictionary.  The 'priorObj'
        is typically set by Orca to be the previous object with
        focus.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        oldLevel = self._script.utilities.nodeLevel(args.get('priorObj', None))
        newLevel = self._script.utilities.nodeLevel(obj)
        if (oldLevel != newLevel) and (newLevel >= 0):
            result.extend(self._generateNodeLevel(obj, **args))
            result.extend(acss)
        return result

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _generatePercentage(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the percentage value of the
        object.  This is typically for progress bars. [[[WDW - we
        should consider returning an empty array if there is no value.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        percentValue = self._script.utilities.getValueAsPercent(obj)
        if percentValue is not None:
            result = [messages.percentage(percentValue)]
            result.extend(self.voice(SYSTEM))
            return result

        return []

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _generateNewRadioButtonGroup(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the radio button group label
        of the object, or an empty array if the object has no such
        label or if the radio button group is not different from the
        'priorObj' 'priorObj' attribute of the args dictionary.  The
        'priorObj' is typically set by Orca to be the previous object
        with focus.
        """
        # [[[TODO: WDW - hate duplicating code from _generateRadioButtonGroup
        # but don't want to call it because it will make the same
        # AT-SPI method calls.]]]
        #
        result = []
        acss = self.voice(DEFAULT)
        priorObj = args.get('priorObj', None)
        if obj and obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            radioGroupLabel = None
            inSameGroup = False
            relations = obj.getRelationSet()
            for relation in relations:
                if (not radioGroupLabel) \
                    and (relation.getRelationType() \
                         == pyatspi.RELATION_LABELLED_BY):
                    radioGroupLabel = relation.getTarget(0)
                if (not inSameGroup) \
                    and (relation.getRelationType() \
                         == pyatspi.RELATION_MEMBER_OF):
                    for i in range(0, relation.getNTargets()):
                        target = relation.getTarget(i)
                        if target == priorObj:
                            inSameGroup = True
                            break
            if (not inSameGroup) and radioGroupLabel:
                result.append(self._script.utilities.\
                                  displayedText(radioGroupLabel))
                result.extend(acss)
        return result

    def _generateNumberOfChildren(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the number of children the
        object has.  [[[WDW - can we always return an empty array if
        this doesn't apply?]]] [[[WDW - I wonder if this string should
        be moved to settings.py.]]]
        """

        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or _settingsManager.getSetting('speechVerbosityLevel') == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        result = []
        acss = self.voice(SYSTEM)
        childNodes = self._script.utilities.childNodes(obj)
        children = len(childNodes)
        if children:
            result.append(messages.itemCount(children))
            result.extend(acss)
            return result

        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_LIST, pyatspi.ROLE_LIST_BOX]:
            children = [x for x in obj if x.getRole() == pyatspi.ROLE_LIST_ITEM]
            setsize = len(children)
            if not setsize:
                return []

            result = [messages.listItemCount(setsize)]
            result.extend(acss)

        return result

    def _generateNoShowingChildren(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if this object has no showing
        children (e.g., it's an empty table or list).  object has.
        [[[WDW - can we always return an empty array if this doesn't
        apply?]]] [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        hasItems = False
        for child in obj:
            state = child.getState()
            if state.contains(pyatspi.STATE_SHOWING):
                hasItems = True
                break
        if not hasItems:
            result.append(messages.ZERO_ITEMS)
            result.extend(acss)
        return result

    def _generateNoChildren(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if this object has no children at
        all (e.g., it's an empty table or list).  object has.  [[[WDW
        - can we always return an empty array if this doesn't
        apply?]]] [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        if not obj.childCount:
            result.append(messages.ZERO_ITEMS)
            result.extend(acss)
        return result

    def _generateFocusedItem(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role not in [pyatspi.ROLE_LIST, pyatspi.ROLE_LIST_BOX]:
            return result

        if 'Selection' in pyatspi.listInterfaces(obj):
            items = self._script.utilities.selectedChildren(obj)
        else:
            items = [self._script.utilities.focusedChild(obj)]
        if not (items and items[0]):
            return result

        for item in map(self._generateName, items):
            result.extend(item)

        return result

    def _generateSelectedItemCount(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) indicating how many items are selected in this
        and the position of the current item. This object will be an icon
        panel or a layered pane.
        """

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        container = obj
        if not 'Selection' in pyatspi.listInterfaces(container):
            container = obj.parent
            if not 'Selection' in pyatspi.listInterfaces(container):
                return []

        result = []
        acss = self.voice(SYSTEM)
        childCount = container.childCount
        selectedCount = len(self._script.utilities.selectedChildren(container))
        result.append(messages.selectedItemsCount(selectedCount, childCount))
        result.extend(acss)
        result.append(self._script.formatting.getString(
                          mode='speech',
                          stringType='iconindex') \
                      % {"index" : obj.getIndexInParent() + 1,
                         "total" : childCount})
        result.extend(acss)
        return result

    def _generateSelectedItems(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the names of all the selected items.
        This object will be an icon panel or a layered pane.
        """

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        container = obj
        if not 'Selection' in pyatspi.listInterfaces(container):
            container = obj.parent
            if not 'Selection' in pyatspi.listInterfaces(container):
                return []

        selectedItems = self._script.utilities.selectedChildren(container)
        return list(map(self._generateLabelAndName, selectedItems))

    def generateSelectedItems(self, obj, **args):
        return self._generateSelectedItems(obj, **args)

    def _generateUnfocusedDialogCount(self, obj,  **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says how many unfocused alerts and
        dialogs are associated with the application for this object.
        [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        # If this application has more than one unfocused alert or
        # dialog window, then speak '<m> unfocused dialogs'
        # to let the user know.
        #
        try:
            alertAndDialogCount = \
                self._script.utilities.unfocusedAlertAndDialogCount(obj)
        except:
            alertAndDialogCount = 0
        if alertAndDialogCount > 0:
            result.append(messages.dialogCountSpeech(alertAndDialogCount))
            result.extend(acss)
        return result

    def _getEnabledAndDisabledContextRoles(self):
        allRoles = [pyatspi.ROLE_BLOCK_QUOTE,
                    'ROLE_CONTENT_DELETION',
                    'ROLE_CONTENT_INSERTION',
                    'ROLE_CONTENT_MARK',
                    'ROLE_CONTENT_SUGGESTION',
                    pyatspi.ROLE_FORM,
                    pyatspi.ROLE_LANDMARK,
                    'ROLE_DPUB_LANDMARK',
                    'ROLE_DPUB_SECTION',
                    pyatspi.ROLE_LIST,
                    pyatspi.ROLE_PANEL,
                    pyatspi.ROLE_TABLE]

        enabled, disabled = [], []
        if self._script.inSayAll():
            if _settingsManager.getSetting('sayAllContextBlockquote'):
                enabled.append(pyatspi.ROLE_BLOCK_QUOTE)
            if _settingsManager.getSetting('sayAllContextLandmark'):
                enabled.extend([pyatspi.ROLE_LANDMARK, 'ROLE_DPUB_LANDMARK'])
            if _settingsManager.getSetting('sayAllContextList'):
                enabled.append(pyatspi.ROLE_LIST)
            if _settingsManager.getSetting('sayAllContextPanel'):
                enabled.extend([pyatspi.ROLE_PANEL,
                                'ROLE_CONTENT_DELETION',
                                'ROLE_CONTENT_INSERTION',
                                'ROLE_CONTENT_MARK',
                                'ROLE_CONTENT_SUGGESTION',
                                'ROLE_DPUB_SECTION'])
            if _settingsManager.getSetting('sayAllContextNonLandmarkForm'):
                enabled.append(pyatspi.ROLE_FORM)
            if _settingsManager.getSetting('sayAllContextTable'):
                enabled.append(pyatspi.ROLE_TABLE)
        else:
            if _settingsManager.getSetting('speakContextBlockquote'):
                enabled.append(pyatspi.ROLE_BLOCK_QUOTE)
            if _settingsManager.getSetting('speakContextLandmark'):
                enabled.extend([pyatspi.ROLE_LANDMARK, 'ROLE_DPUB_LANDMARK'])
            if _settingsManager.getSetting('speakContextList'):
                enabled.append(pyatspi.ROLE_LIST)
            if _settingsManager.getSetting('speakContextPanel'):
                enabled.extend([pyatspi.ROLE_PANEL,
                                'ROLE_CONTENT_DELETION',
                                'ROLE_CONTENT_INSERTION',
                                'ROLE_CONTENT_MARK',
                                'ROLE_CONTENT_SUGGESTION',
                                'ROLE_DPUB_SECTION'])
            if _settingsManager.getSetting('speakContextNonLandmarkForm'):
                enabled.append(pyatspi.ROLE_FORM)
            if _settingsManager.getSetting('speakContextTable'):
                enabled.append(pyatspi.ROLE_TABLE)

        disabled = list(set(allRoles).symmetric_difference(enabled))
        return enabled, disabled

    def _generateLeaving(self, obj, **args):
        if not args.get('leaving'):
            return []

        role = args.get('role', obj.getRole())
        enabled, disabled = self._getEnabledAndDisabledContextRoles()
        if not (role in enabled or self._script.utilities.isDetails(obj)):
            return []

        count = args.get('count', 1)

        result = []
        if self._script.utilities.isDetails(obj):
            result.append(messages.LEAVING_DETAILS)
        elif role == pyatspi.ROLE_BLOCK_QUOTE:
            if count > 1:
                result.append(messages.leavingNBlockquotes(count))
            else:
                result.append(messages.LEAVING_BLOCKQUOTE)
        elif role == pyatspi.ROLE_LIST and self._script.utilities.isDocumentList(obj):
            if count > 1:
                result.append(messages.leavingNLists(count))
            else:
                result.append(messages.LEAVING_LIST)
        elif role == pyatspi.ROLE_PANEL:
            if self._script.utilities.isFeed(obj):
                result.append(messages.LEAVING_FEED)
            elif self._script.utilities.isFigure(obj):
                result.append(messages.LEAVING_FIGURE)
            elif self._script.utilities.isDocumentPanel(obj):
                result.append(messages.LEAVING_PANEL)
            else:
                result = ['']
        elif role == pyatspi.ROLE_TABLE and self._script.utilities.isTextDocumentTable(obj):
            result.append(messages.LEAVING_TABLE)
        elif role == 'ROLE_DPUB_LANDMARK':
            if self._script.utilities.isDPubAcknowledgments(obj):
                result.append(messages.LEAVING_ACKNOWLEDGMENTS)
            elif self._script.utilities.isDPubAfterword(obj):
                result.append(messages.LEAVING_AFTERWORD)
            elif self._script.utilities.isDPubAppendix(obj):
                result.append(messages.LEAVING_APPENDIX)
            elif self._script.utilities.isDPubBibliography(obj):
                result.append(messages.LEAVING_BIBLIOGRAPHY)
            elif self._script.utilities.isDPubChapter(obj):
                result.append(messages.LEAVING_CHAPTER)
            elif self._script.utilities.isDPubConclusion(obj):
                result.append(messages.LEAVING_CONCLUSION)
            elif self._script.utilities.isDPubCredits(obj):
                result.append(messages.LEAVING_CREDITS)
            elif self._script.utilities.isDPubEndnotes(obj):
                result.append(messages.LEAVING_ENDNOTES)
            elif self._script.utilities.isDPubEpilogue(obj):
                result.append(messages.LEAVING_EPILOGUE)
            elif self._script.utilities.isDPubErrata(obj):
                result.append(messages.LEAVING_ERRATA)
            elif self._script.utilities.isDPubForeword(obj):
                result.append(messages.LEAVING_FOREWORD)
            elif self._script.utilities.isDPubGlossary(obj):
                result.append(messages.LEAVING_GLOSSARY)
            elif self._script.utilities.isDPubIndex(obj):
                result.append(messages.LEAVING_INDEX)
            elif self._script.utilities.isDPubIntroduction(obj):
                result.append(messages.LEAVING_INTRODUCTION)
            elif self._script.utilities.isDPubPagelist(obj):
                result.append(messages.LEAVING_PAGELIST)
            elif self._script.utilities.isDPubPart(obj):
                result.append(messages.LEAVING_PART)
            elif self._script.utilities.isDPubPreface(obj):
                result.append(messages.LEAVING_PREFACE)
            elif self._script.utilities.isDPubPrologue(obj):
                result.append(messages.LEAVING_PROLOGUE)
            elif self._script.utilities.isDPubToc(obj):
                result.append(messages.LEAVING_TOC)
        elif role == 'ROLE_DPUB_SECTION':
            if self._script.utilities.isDPubAbstract(obj):
                result.append(messages.LEAVING_ABSTRACT)
            elif self._script.utilities.isDPubColophon(obj):
                result.append(messages.LEAVING_COLOPHON)
            elif self._script.utilities.isDPubCredit(obj):
                result.append(messages.LEAVING_CREDIT)
            elif self._script.utilities.isDPubDedication(obj):
                result.append(messages.LEAVING_DEDICATION)
            elif self._script.utilities.isDPubEpigraph(obj):
                result.append(messages.LEAVING_EPIGRAPH)
            elif self._script.utilities.isDPubExample(obj):
                result.append(messages.LEAVING_EXAMPLE)
            elif self._script.utilities.isDPubPullquote(obj):
                result.append(messages.LEAVING_PULLQUOTE)
            elif self._script.utilities.isDPubQna(obj):
                result.append(messages.LEAVING_QNA)
        elif self._script.utilities.isLandmark(obj):
            if self._script.utilities.isLandmarkBanner(obj):
                result.append(messages.LEAVING_LANDMARK_BANNER)
            elif self._script.utilities.isLandmarkComplementary(obj):
                result.append(messages.LEAVING_LANDMARK_COMPLEMENTARY)
            elif self._script.utilities.isLandmarkContentInfo(obj):
                result.append(messages.LEAVING_LANDMARK_CONTENTINFO)
            elif self._script.utilities.isLandmarkMain(obj):
                result.append(messages.LEAVING_LANDMARK_MAIN)
            elif self._script.utilities.isLandmarkNavigation(obj):
                result.append(messages.LEAVING_LANDMARK_NAVIGATION)
            elif self._script.utilities.isLandmarkRegion(obj):
                result.append(messages.LEAVING_LANDMARK_REGION)
            elif self._script.utilities.isLandmarkSearch(obj):
                result.append(messages.LEAVING_LANDMARK_SEARCH)
            elif self._script.utilities.isLandmarkForm(obj):
                result.append(messages.LEAVING_FORM)
            else:
                result = ['']
        elif role == pyatspi.ROLE_FORM:
            result.append(messages.LEAVING_FORM)
        elif role == 'ROLE_CONTENT_DELETION':
            result.append(messages.CONTENT_DELETION_END)
        elif role == 'ROLE_CONTENT_INSERTION':
            result.append(messages.CONTENT_INSERTION_END)
        elif role == 'ROLE_CONTENT_MARK':
            result.append(messages.CONTENT_MARK_END)
        elif role == 'ROLE_CONTENT_SUGGESTION' \
             and not self._script.utilities.isInlineSuggestion(obj):
            result.append(messages.LEAVING_SUGGESTION)
        else:
            result = ['']
        if result:
            result.extend(self.voice(SYSTEM))

        return result

    def _generateAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object.  This is typically used to present the context for
        an object (e.g., the names of the window, the panels, etc.,
        that the object is contained in).  If the 'priorObj' attribute
        of the args dictionary is set, only the differences in
        ancestry between the 'priorObj' and the current obj will be
        computed.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """
        result = []

        leaving = args.get('leaving')
        if leaving and args.get('priorObj'):
              priorObj = obj
              obj = args.get('priorObj')
        else:
              priorObj = args.get('priorObj')

        if priorObj and self._script.utilities.isDead(priorObj):
            return []

        if priorObj and priorObj.getRole() == pyatspi.ROLE_TOOL_TIP:
            return []

        if priorObj and priorObj.parent == obj.parent:
            return []

        if self._script.utilities.isTypeahead(priorObj):
            return []

        commonAncestor = self._script.utilities.commonAncestor(priorObj, obj)
        if obj == commonAncestor:
            return []

        includeOnly = args.get('includeOnly', [])

        skipRoles = args.get('skipRoles', [])
        skipRoles.append(pyatspi.ROLE_TREE_ITEM)
        enabled, disabled = self._getEnabledAndDisabledContextRoles()
        skipRoles.extend(disabled)

        stopAtRoles = args.get('stopAtRoles', [])
        stopAtRoles.extend([pyatspi.ROLE_APPLICATION, pyatspi.ROLE_MENU_BAR])

        presentOnce = [pyatspi.ROLE_BLOCK_QUOTE, pyatspi.ROLE_LIST]

        presentCommonAncestor = False
        if commonAncestor and not leaving:
            commonRole = self._getAlternativeRole(commonAncestor)
            if commonRole in presentOnce:
                pred = lambda x: x and self._getAlternativeRole(x) == commonRole
                objAncestor = pyatspi.findAncestor(obj, pred)
                priorAncestor = pyatspi.findAncestor(priorObj, pred)
                objLevel = self._script.utilities.nestingLevel(objAncestor)
                priorLevel = self._script.utilities.nestingLevel(priorAncestor)
                presentCommonAncestor = objLevel != priorLevel

        ancestors, ancestorRoles = [], []
        parent = obj.parent
        while parent and parent != parent.parent:
            parentRole = self._getAlternativeRole(parent)
            if parentRole in stopAtRoles:
                break
            if parentRole in skipRoles:
                pass
            elif includeOnly and parentRole not in includeOnly:
                pass
            elif self._script.utilities.isLayoutOnly(parent):
                pass
            elif self._script.utilities.isButtonWithPopup(parent):
                pass
            elif parent != commonAncestor or presentCommonAncestor:
                ancestors.append(parent)
                ancestorRoles.append(parentRole)

            if parent == commonAncestor:
                break

            parent = parent.parent

        presentedRoles = []
        for i, x in enumerate(ancestors):
            altRole = ancestorRoles[i]
            if altRole in presentOnce and altRole in presentedRoles:
                continue

            presentedRoles.append(altRole)
            count = ancestorRoles.count(altRole)
            self._overrideRole(altRole, args)
            result.append(self.generate(x, formatType='focused', role=altRole, leaving=leaving, count=count))
            self._restoreRole(altRole, args)

        if not leaving:
            result.reverse()
        return result

    def _generateOldAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object being left."""

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if self._script.utilities.inFindContainer():
            return []

        priorObj = args.get('priorObj')
        if not priorObj or obj == priorObj or self._script.utilities.isZombie(priorObj):
            return []

        if obj.getRole() == pyatspi.ROLE_PAGE_TAB:
            return []

        if obj.getApplication() != priorObj.getApplication() \
           or pyatspi.findAncestor(obj, lambda x: x == priorObj):
            return []

        frame, dialog = self._script.utilities.frameAndDialog(obj)
        if dialog:
            return []

        args['leaving'] = True
        args['includeOnly'] = [pyatspi.ROLE_BLOCK_QUOTE,
                               pyatspi.ROLE_FORM,
                               pyatspi.ROLE_LANDMARK,
                               'ROLE_CONTENT_DELETION',
                               'ROLE_CONTENT_INSERTION',
                               'ROLE_CONTENT_MARK',
                               'ROLE_CONTENT_SUGGESTION',
                               'ROLE_DPUB_LANDMARK',
                               'ROLE_DPUB_SECTION',
                               pyatspi.ROLE_LIST,
                               pyatspi.ROLE_PANEL,
                               pyatspi.ROLE_TABLE]

        result = []
        if self._script.utilities.isBlockquote(priorObj):
            oldRole = self._getAlternativeRole(priorObj)
            self._overrideRole(oldRole, args)
            result.extend(self.generate(
                priorObj, role=oldRole, formatType='focused', leaving=True))
            self._restoreRole(oldRole, args)

        result.extend(self._generateAncestors(obj, **args))
        args.pop('leaving')
        args.pop('includeOnly')

        return result

    def _generateNewAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object.  This is typically used to present the context for
        an object (e.g., the names of the window, the panels, etc.,
        that the object is contained in).  If the 'priorObj' attribute
        of the args dictionary is set, only the differences in
        ancestry between the 'priorObj' and the current obj will be
        computed.  Otherwise, no ancestry will be computed.  The
        'priorObj' is typically set by Orca to be the previous object
        with focus.
        """

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if self._script.utilities.inFindContainer():
            return []

        priorObj = args.get('priorObj')
        if priorObj == obj:
            return []

        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_FRAME, pyatspi.ROLE_WINDOW]:
            return []

        result = []
        if role == pyatspi.ROLE_MENU_ITEM \
           and (not priorObj or priorObj.getRole() == pyatspi.ROLE_WINDOW):
            return result

        topLevelObj = self._script.utilities.topLevelObject(obj)
        if priorObj \
           or (topLevelObj and topLevelObj.getRole() == pyatspi.ROLE_DIALOG):
            result = self._generateAncestors(obj, **args)
        return result

    def generateContext(self, obj, **args):
        if args.get('priorObj') == obj:
            return []

        result = self._generateOldAncestors(obj, **args)
        result.append(self._generateNewAncestors(obj, **args))
        return result

    def _generateParentRoleName(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the role name of the parent of obj.
        """
        if args.get('role', obj.getRole()) == pyatspi.ROLE_ICON \
           and args.get('formatType', None) \
               in ['basicWhereAmI', 'detailedWhereAmI']:
            return [object_properties.ROLE_ICON_PANEL]
        if obj.parent.getRole() in [pyatspi.ROLE_TABLE_CELL, pyatspi.ROLE_MENU]:
            obj = obj.parent
        return self._generateRoleName(obj.parent)

    def _generateToolbar(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the name and role of the toolbar
        which contains obj.
        """
        result = []
        ancestor = self._script.utilities.ancestorWithRole(
            obj, [pyatspi.ROLE_TOOL_BAR], [pyatspi.ROLE_FRAME])
        if ancestor:
            result.extend(self._generateLabelAndName(ancestor))
            result.extend(self._generateRoleName(ancestor))
        return result

    def _generatePositionInGroup(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a group.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        position = -1
        total = -1

        try:
            relations = obj.getRelationSet()
        except:
            relations = []
        for relation in relations:
            if relation.getRelationType() == pyatspi.RELATION_MEMBER_OF:
                total = 0
                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    if target.getState().contains(pyatspi.STATE_SHOWING):
                        total += 1
                        if target == obj:
                            position = total

        if position >= 0:
            # Adjust the position because the relations tend to be given
            # in the reverse order.
            position = total - position + 1
            result.append(self._script.formatting.getString(
                              mode='speech',
                              stringType='groupindex') \
                          % {"index" : position,
                             "total" : total})
            result.extend(acss)
        return result

    def _generatePositionInList(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a list.
        """

        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or not (_settingsManager.getSetting('enablePositionSpeaking') \
                   or args.get('forceList', False)):
            return []

        if self._script.utilities.isTopLevelMenu(obj):
            return []

        if self._script.utilities.isEditableComboBox(obj):
            return []

        result = []
        acss = self.voice(SYSTEM)
        position, total = self._script.utilities.getPositionAndSetSize(obj, **args)
        if position < 0 or total < 0:
            return []

        position += 1
        result.append(self._script.formatting.getString(
                              mode='speech',
                              stringType='groupindex') \
                          % {"index" : position,
                             "total" : total})
        result.extend(acss)
        return result

    def _generateProgressBarIndex(self, obj, **args):
        if not args.get('isProgressBarUpdate') \
           or not self._shouldPresentProgressBarUpdate(obj, **args):
            return []

        result = []
        acc, updateTime, updateValue = self._getMostRecentProgressBarUpdate()
        if acc != obj:
            number, count = self.getProgressBarNumberAndCount(obj)
            result = [messages.PROGRESS_BAR_NUMBER % (number)]
            result.extend(self.voice(SYSTEM))

        return result

    def _generateProgressBarValue(self, obj, **args):
        if args.get('isProgressBarUpdate') \
           and not self._shouldPresentProgressBarUpdate(obj, **args):
            return []

        result = []
        percent = self._script.utilities.getValueAsPercent(obj)
        if percent is not None:
            result.append(messages.percentage(percent))
            result.extend(self.voice(SYSTEM))

        return result

    def _getProgressBarUpdateInterval(self):
        interval = _settingsManager.getSetting('progressBarSpeechInterval')
        if interval is None:
            interval = super()._getProgressBarUpdateInterval()

        return int(interval)

    def _shouldPresentProgressBarUpdate(self, obj, **args):
        if not _settingsManager.getSetting('speakProgressBarUpdates'):
            return False

        return super()._shouldPresentProgressBarUpdate(obj, **args)

    def _generateDefaultButton(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the default button in a dialog.
        This method should initially be called with a top-level window.
        """
        result = []
        button = self._script.utilities.defaultButton(obj)
        if button and button.getState().contains(pyatspi.STATE_SENSITIVE):
            name = self._generateName(button)
            if name:
                result.append(messages.DEFAULT_BUTTON_IS % name[0])
                result.extend(self.voice(SYSTEM))

        return result

    def generateDefaultButton(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the default button of the window
        containing the object.
        """
        return self._generateDefaultButton(obj, **args)

    def _generateStatusBar(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the status bar of a window.
        This method should initially be called with a top-level window.
        """

        statusBar = self._script.utilities.statusBar(obj)
        if not statusBar:
            return []

        result = self._generateName(statusBar)
        if result:
            return result

        for child in statusBar:
            childResult = self._generateDisplayedText(child)
            if not childResult and child.getRole() != pyatspi.ROLE_LABEL:
                childResult = self.generate(child, includeContext=False)
            if childResult:
                result.extend(childResult)

        return result

    def generateStatusBar(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the status bar of the window
        containing the object.
        """
        return self._generateStatusBar(obj, **args)

    def generateTitle(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the title of the window, obj.
        containing the object, along with information associated with
        any unfocused dialog boxes.
        """
        result = []
        acss = self.voice(DEFAULT)
        frame, dialog = self._script.utilities.frameAndDialog(obj)
        if frame:
            frameResult = self._generateLabelAndName(frame)
            if not frameResult:
                frameResult = self._generateRoleName(frame)
            result.append(frameResult)

        if dialog:
            result.append(self._generateLabelAndName(dialog))

        alertAndDialogCount = self._script.utilities.unfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            dialogs = [messages.dialogCountSpeech(alertAndDialogCount)]
            dialogs.extend(acss)
            result.append(dialogs)
        return result

    def _generateListBoxItemWidgets(self, obj, **args):
        widgetRoles = [pyatspi.ROLE_CHECK_BOX,
                       pyatspi.ROLE_COMBO_BOX,
                       pyatspi.ROLE_PUSH_BUTTON,
                       pyatspi.ROLE_RADIO_BUTTON,
                       pyatspi.ROLE_SLIDER,
                       pyatspi.ROLE_TEXT,
                       pyatspi.ROLE_TOGGLE_BUTTON]
        isWidget = lambda x: x and x.getRole() in widgetRoles
        result = []
        if obj.parent and obj.parent.getRole() == pyatspi.ROLE_LIST_BOX:
            widgets = self._script.utilities.findAllDescendants(obj, isWidget)
            for widget in widgets:
                if self._script.utilities.isShowingAndVisible(widget):
                    result.append(self.generate(widget, includeContext=False))

        return result

    #####################################################################
    #                                                                   #
    # Keyboard shortcut information                                     #
    #                                                                   #
    #####################################################################

    def _generateAccelerator(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the accelerator for the object,
        or an empty array if no accelerator can be found.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        [mnemonic, shortcut, accelerator] = \
            self._script.utilities.mnemonicShortcutAccelerator(obj)
        if accelerator:
            result.append(accelerator)
            result.extend(acss)

        return result

    def _generateMnemonic(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the mnemonic for the object, or
        an empty array if no mnemonic can be found.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        if _settingsManager.getSetting('enableMnemonicSpeaking') \
           or args.get('forceMnemonic', False):
            [mnemonic, shortcut, accelerator] = \
                self._script.utilities.mnemonicShortcutAccelerator(obj)
            if mnemonic:
                mnemonic = mnemonic[-1] # we just want a single character
            if not mnemonic and shortcut:
                mnemonic = shortcut
            if mnemonic:
                result = [mnemonic]
                result.extend(acss)

        return result

    #####################################################################
    #                                                                   #
    # Tutorial information                                              #
    #                                                                   #
    #####################################################################

    def _generateTutorial(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the tutorial for the object.
        The tutorial will only be generated if the user has requested
        tutorials, and will then be generated according to the
        tutorial generator.  A tutorial can be forced by setting the
        'forceTutorial' attribute of the args dictionary to True.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        alreadyFocused = args.get('alreadyFocused', False)
        forceTutorial = args.get('forceTutorial', False)
        role = args.get('role', obj.getRole())
        result.extend(self._script.tutorialGenerator.getTutorial(
                obj,
                alreadyFocused,
                forceTutorial,
                role))
        if args.get('role', obj.getRole()) == pyatspi.ROLE_ICON \
            and args.get('formatType', 'unfocused') == 'basicWhereAmI':
            frame, dialog = self._script.utilities.frameAndDialog(obj)
            if frame:
                result.extend(self._script.tutorialGenerator.getTutorial(
                        frame,
                        alreadyFocused,
                        forceTutorial))
        if result and result[0]:
            result.extend(acss)
        return result

    # Math

    def _generateMath(self, obj, **args):
        result = []
        children = [child for child in obj] or [obj]
        for child in children:
            if self._script.utilities.isMathLayoutOnly(child) and child.childCount:
                result.extend(self._generateMath(child))
                continue

            oldRole = self._getAlternativeRole(child)
            self._overrideRole(oldRole, args)
            result.extend(self.generate(child, role=oldRole))
            self._restoreRole(oldRole, args)

        return result

    def _generateEnclosedBase(self, obj, **args):
        return self._generateMath(obj, **args)

    def _generateEnclosedEnclosures(self, obj, **args):
        strings = []
        enclosures = self._script.utilities.getMathEnclosures(obj)
        if 'actuarial' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_ACTUARIAL)
        if 'box' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_BOX)
        if 'circle' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_CIRCLE)
        if 'longdiv' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_LONGDIV)
        if 'radical' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_RADICAL)
        if 'roundedbox' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_ROUNDEDBOX)
        if 'horizontalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_HORIZONTALSTRIKE)
        if 'verticalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_VERTICALSTRIKE)
        if 'downdiagonalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_DOWNDIAGONALSTRIKE)
        if 'updiagonalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_UPDIAGONALSTRIKE)
        if 'northeastarrow' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_NORTHEASTARROW)
        if 'bottom' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_BOTTOM)
        if 'left' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_LEFT)
        if 'right' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_RIGHT)
        if 'top' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_TOP)
        if 'phasorangle' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_PHASOR_ANGLE)
        if 'madruwb' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_MADRUWB)
        if not strings:
            msg = 'INFO: Could not get enclosure message for %s' % enclosures
            debug.println(debug.LEVEL_INFO, msg)
            return []

        if len(strings) == 1:
            result = [messages.MATH_ENCLOSURE_ENCLOSED_BY % strings[0]]
        else:
            strings.insert(-1, messages.MATH_ENCLOSURE_AND)
            if len(strings) == 3:
                result = [messages.MATH_ENCLOSURE_ENCLOSED_BY % " ".join(strings)]
            else:
                result = [messages.MATH_ENCLOSURE_ENCLOSED_BY % ", ".join(strings)]

        result.extend(self.voice(SYSTEM))
        return result

    def _generateFencedStart(self, obj, **args):
        fenceStart, fenceEnd = self._script.utilities.getMathFences(obj)
        if fenceStart:
            result = [chnames.getCharacterName(fenceStart)]
            result.extend(self.voice(DEFAULT))
            return result

        return []

    def _generateFencedContents(self, obj, **args):
        result = []
        separators = self._script.utilities.getMathFencedSeparators(obj)
        for x in range(len(separators), obj.childCount-1):
            separators.append(separators[-1])
        separators.append('')

        for i, child in enumerate(obj):
            result.extend(self._generateMath(child, **args))
            separatorName = chnames.getCharacterName(separators[i])
            result.append(separatorName)
            result.extend(self.voice(DEFAULT))
            if separatorName:
                result.extend(self._generatePause(obj, **args))

        return result

    def _generateFencedEnd(self, obj, **args):
        fenceStart, fenceEnd = self._script.utilities.getMathFences(obj)
        if fenceEnd:
            result = [chnames.getCharacterName(fenceEnd)]
            result.extend(self.voice(DEFAULT))
            return result

        return []

    def _generateFractionStart(self, obj, **args):
        if self._script.utilities.isMathFractionWithoutBar(obj):
            result = [messages.MATH_FRACTION_WITHOUT_BAR_START]
        else:
            result = [messages.MATH_FRACTION_START]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateFractionNumerator(self, obj, **args):
        numerator = self._script.utilities.getMathNumerator(obj)
        if self._script.utilities.isMathLayoutOnly(numerator):
            return self._generateMath(numerator)

        oldRole = self._getAlternativeRole(numerator)
        self._overrideRole(oldRole, args)
        result = self.generate(numerator, role=oldRole)
        self._restoreRole(oldRole, args)
        return result

    def _generateFractionDenominator(self, obj, **args):
        denominator = self._script.utilities.getMathDenominator(obj)
        if self._script.utilities.isMathLayoutOnly(denominator):
            return self._generateMath(denominator)

        oldRole = self._getAlternativeRole(denominator)
        self._overrideRole(oldRole, args)
        result = self.generate(denominator, role=oldRole)
        self._restoreRole(oldRole, args)
        return result

    def _generateFractionLine(self, obj, **args):
        result = [messages.MATH_FRACTION_LINE]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateFractionEnd(self, obj, **args):
        result = [messages.MATH_FRACTION_END]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateRootStart(self, obj, **args):
        result = []
        if self._script.utilities.isMathSquareRoot(obj):
            result = [messages.MATH_SQUARE_ROOT_OF]
        else:
            index = self._script.utilities.getMathRootIndex(obj)
            string = self._script.utilities.displayedText(index)
            if string == "2":
                result = [messages.MATH_SQUARE_ROOT_OF]
            elif string == "3":
                result = [messages.MATH_CUBE_ROOT_OF]
            elif string:
                result = [string]
                result.extend([messages.MATH_ROOT_OF])
            elif self._script.utilities.isMathLayoutOnly(index):
                result = self._generateMath(index)
                result.extend([messages.MATH_ROOT_OF])
            else:
                oldRole = self._getAlternativeRole(index)
                self._overrideRole(oldRole, args)
                result.extend(self.generate(index, role=oldRole))
                self._restoreRole(oldRole, args)
                result.extend([messages.MATH_ROOT_OF])

        if result:
            result.extend(self.voice(SYSTEM))

        return result

    def _generateRootBase(self, obj, **args):
        base = self._script.utilities.getMathRootBase(obj)
        if not base:
            return []

        if self._script.utilities.isMathSquareRoot(obj) \
           or self._script.utilities.isMathToken(base) \
           or self._script.utilities.isMathLayoutOnly(base):
            return self._generateMath(base)

        result = [self._generatePause(obj, **args)]
        oldRole = self._getAlternativeRole(base)
        self._overrideRole(oldRole, args)
        result.extend(self.generate(base, role=oldRole))
        self._restoreRole(oldRole, args)

        return result

    def _generateRootEnd(self, obj, **args):
        result = [messages.MATH_ROOT_END]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateScriptBase(self, obj, **args):
        base = self._script.utilities.getMathScriptBase(obj)
        if not base:
            return []

        return self._generateMath(base)

    def _generateScriptScript(self, obj, **args):
        if self._script.utilities.isMathLayoutOnly(obj):
            return self._generateMath(obj)

        oldRole = self._getAlternativeRole(obj)
        self._overrideRole(oldRole, args)
        result = self.generate(obj, role=oldRole)
        self._restoreRole(oldRole, args)

        return result

    def _generateScriptSubscript(self, obj, **args):
        subscript = self._script.utilities.getMathScriptSubscript(obj)
        if not subscript:
            return []

        result = [messages.MATH_SUBSCRIPT]
        result.extend(self.voice(SYSTEM))
        result.extend(self._generateScriptScript(subscript))

        return result

    def _generateScriptSuperscript(self, obj, **args):
        superscript = self._script.utilities.getMathScriptSuperscript(obj)
        if not superscript:
            return []

        result = [messages.MATH_SUPERSCRIPT]
        result.extend(self.voice(SYSTEM))
        result.extend(self._generateScriptScript(superscript))

        return result

    def _generateScriptUnderscript(self, obj, **args):
        underscript = self._script.utilities.getMathScriptUnderscript(obj)
        if not underscript:
            return []

        result = [messages.MATH_UNDERSCRIPT]
        result.extend(self.voice(SYSTEM))
        result.extend(self._generateScriptScript(underscript))

        return result

    def _generateScriptOverscript(self, obj, **args):
        overscript = self._script.utilities.getMathScriptOverscript(obj)
        if not overscript:
            return []

        result = [messages.MATH_OVERSCRIPT]
        result.extend(self.voice(SYSTEM))
        result.extend(self._generateScriptScript(overscript))

        return result

    def _generateScriptPrescripts(self, obj, **args):
        result = []
        prescripts = self._script.utilities.getMathPrescripts(obj)
        for i, script in enumerate(prescripts):
            if self._script.utilities.isNoneElement(script):
                continue
            if i % 2:
                rv = [messages.MATH_PRE_SUPERSCRIPT]
            else:
                rv = [messages.MATH_PRE_SUBSCRIPT]
            rv.extend(self.voice(SYSTEM))
            rv.extend(self._generateScriptScript(script))
            result.append(rv)

        return result

    def _generateScriptPostscripts(self, obj, **args):
        result = []
        postscripts = self._script.utilities.getMathPostscripts(obj)
        for i, script in enumerate(postscripts):
            if self._script.utilities.isNoneElement(script):
                continue
            if i % 2:
                rv = [messages.MATH_SUPERSCRIPT]
            else:
                rv = [messages.MATH_SUBSCRIPT]
            rv.extend(self.voice(SYSTEM))
            rv.extend(self._generateScriptScript(script))
            result.append(rv)

        return result

    def _generateMathTableStart(self, obj, **args):
        try:
            table = obj.queryTable()
        except:
            return []

        nestingLevel = self._script.utilities.getMathNestingLevel(obj)
        if nestingLevel > 0:
            result = [messages.mathNestedTableSize(table.nRows, table.nColumns)]
        else:
            result = [messages.mathTableSize(table.nRows, table.nColumns)]
        result.extend(self.voice(SYSTEM))
        return result

    def _generateMathTableRows(self, obj, **args):
        result = []
        for row in obj:
            oldRole = self._getAlternativeRole(row)
            self._overrideRole(oldRole, args)
            result.extend(self.generate(row, role=oldRole))
            self._restoreRole(oldRole, args)

        return result

    def _generateMathRow(self, obj, **args):
        result = []

        result.append(messages.TABLE_ROW % (obj.getIndexInParent() + 1))
        result.extend(self.voice(SYSTEM))
        result.extend(self._generatePause(obj, **args))

        for child in obj:
            result.extend(self._generateMath(child))
            result.extend(self._generatePause(child, **args))

        return result

    def _generateMathTableEnd(self, obj, **args):
        nestingLevel = self._script.utilities.getMathNestingLevel(obj)
        if nestingLevel > 0:
            result = [messages.MATH_NESTED_TABLE_END]
        else:
            result = [messages.MATH_TABLE_END]
        result.extend(self.voice(SYSTEM))
        return result

    #####################################################################
    #                                                                   #
    # Other things for prosody and voice selection                      #
    #                                                                   #
    #####################################################################

    def _generatePause(self, obj, **args):
        if not _settingsManager.getSetting('enablePauseBreaks') \
           or args.get('eliminatePauses', False):
            return []

        if _settingsManager.getSetting('verbalizePunctuationStyle') == \
           settings.PUNCTUATION_STYLE_ALL:
            return []

        return PAUSE

    def _generateLineBreak(self, obj, **args):
        return LINE_BREAK

    def voice(self, key=None, **args):
        """Returns an array containing a voice.  The key is a value
        to be used to look up the voice in the settings.py:voices
        dictionary. Other arguments can be passed in for future
        decision making.
        """

        voicename = voiceType.get(key) or voiceType.get(DEFAULT)
        voices = _settingsManager.getSetting('voices')
        voice = acss.ACSS(voices.get(voiceType.get(DEFAULT)))

        if key in [None, DEFAULT]:
            string = args.get('string', '')
            if isinstance(string, str) and string.isupper():
                voice.update(voices.get(voiceType.get(UPPERCASE)))
        else:
            override = voices.get(voicename)
            if override and override.get('established', True):
                voice.update(override)

        return [voice]

    def utterancesToString(self, utterances):
        string = ""
        for u in utterances:
            if isinstance(u, str):
                string += " %s" % u
            elif isinstance(u, Pause) and string and string[-1].isalnum():
                string += "."

        return string.strip()
