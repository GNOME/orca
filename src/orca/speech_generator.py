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
from gi.repository import Atspi, Atk

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
        if not result and obj.parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
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

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateDescription(self, obj, **args)
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

    def _generateAvailability(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        result = generator.Generator._generateAvailability(self, obj, **args)
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

        if _settingsManager.getSetting('speechVerbosityLevel') == \
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

        result = []
        acss = self.voice(SYSTEM)
        role = args.get('role', obj.getRole())

        doNotPresent = [pyatspi.ROLE_UNKNOWN,
                        pyatspi.ROLE_FILLER,
                        pyatspi.ROLE_EXTENDED]

        try:
            parentRole = obj.parent.getRole()
        except:
            parentRole = None

        if role == pyatspi.ROLE_MENU and parentRole == pyatspi.ROLE_COMBO_BOX:
            return self._generateRoleName(obj.parent)

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
                    'role': self.getLocalizedRoleName(obj, role),
                    'level': level})
                result.extend(acss)

        if role not in doNotPresent and not result:
            result.append(self.getLocalizedRoleName(obj, role))
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
        return self._generateRoleName(obj, **args)

    def getLocalizedRoleName(self, obj, role=None):
        """Returns the localized name of the given Accessible object; the name
        is suitable to be spoken.

        Arguments:
        - obj: an Accessible object
        - role: an optional pyatspi role to use instead
        """

        if not isinstance(role, pyatspi.Role):
            try:
                return obj.getLocalizedRoleName()
            except:
                return ''

        if not role:
            return ''

        nonlocalized = Atspi.role_get_name(role)
        atkRole = Atk.role_for_name(nonlocalized)

        return Atk.role_get_localized_name(atkRole)

    def _generateUnrelatedLabels(self, obj, **args):
        """Returns, as an array of strings (and possibly voice
        specifications), all the labels which are underneath the obj's
        hierarchy and which are not in a label for or labelled by
        relation.
        """
        result = []
        acss = self.voice(DEFAULT)
        visibleOnly = not self._script.utilities.isStatusBarNotification(obj)
        labels = self._script.utilities.unrelatedLabels(obj, visibleOnly)
        for label in labels:
            name = self._generateName(label, **args)
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
        the object.  This is typically for check boxes. If the object
        is not multiselectable, an empty array will be returned.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(STATE)
        if obj.getState().contains(pyatspi.STATE_MULTISELECTABLE) \
           and obj.childCount:
            result.append(self._script.formatting.getString(
                mode='speech',
                stringType='multiselect'))
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
        result = []
        acss = self.voice(DEFAULT)
        if obj:
            priorObj = args.get('priorObj', None)
            try:
                priorParent = priorObj.parent
            except:
                priorParent = None

            if (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                or (obj.parent and obj.parent.getRole() == pyatspi.ROLE_TABLE):
                try:
                    table = priorParent.queryTable()
                except:
                    table = None
                if table \
                   and ((priorObj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                         or (priorObj.getRole() == pyatspi.ROLE_TABLE)):
                    index = self._script.utilities.cellIndex(priorObj)
                    oldRow = table.getRowAtIndex(index)
                else:
                    oldRow = -1

                try:
                    table = obj.parent.queryTable()
                except:
                    pass
                else:
                    index = self._script.utilities.cellIndex(obj)
                    newRow = table.getRowAtIndex(index)
                    if (newRow >= 0) \
                       and (index != newRow) \
                       and ((newRow != oldRow) \
                            or (obj.parent != priorParent)):
                        result = self._generateRowHeader(obj, **args)
        if result:
            result.extend(acss)
        return result

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
        result = []
        acss = self.voice(DEFAULT)
        if obj and not args.get('readingRow', False):
            priorObj = args.get('priorObj', None)
            try:
                priorParent = priorObj.parent
            except:
                priorParent = None

            if (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                or (obj.parent and obj.parent.getRole() == pyatspi.ROLE_TABLE):
                try:
                    table = priorParent.queryTable()
                except:
                    table = None
                if table \
                   and ((priorObj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                         or (priorObj.getRole() == pyatspi.ROLE_TABLE)):
                    index = self._script.utilities.cellIndex(priorObj)
                    oldCol = table.getColumnAtIndex(index)
                else:
                    oldCol = -1

                try:
                    table = obj.parent.queryTable()
                except:
                    pass
                else:
                    index = self._script.utilities.cellIndex(obj)
                    newCol = table.getColumnAtIndex(index)
                    if (newCol >= 0) \
                       and (index != newCol) \
                       and ((newCol != oldCol) \
                            or (obj.parent != priorParent)):
                        result = self._generateColumnHeader(obj, **args)
        if result:
            result.extend(acss)
        return result

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
        if not result and _settingsManager.getSetting('speakBlankLines') \
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

        if not obj:
            return []

        if not (obj.parent and 'Selection' in pyatspi.listInterfaces(obj.parent)):
            return []

        state = obj.getState()
        if state.contains(pyatspi.STATE_SELECTED):
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

        result = []
        acss = self.voice(SYSTEM)
        if _settingsManager.getSetting('speechVerbosityLevel') \
                == settings.VERBOSITY_LEVEL_VERBOSE:
            if obj.getRole() == pyatspi.ROLE_TABLE_CELL:
                cell = obj
            else:
                cell = self._script.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_TABLE_CELL], [pyatspi.ROLE_FRAME])
            try:
                table = cell.parent.queryTable()
            except:
                pass
            else:
                index = self._script.utilities.cellIndex(cell)
                row = table.getRowAtIndex(index)
                col = table.getColumnAtIndex(index)
                if row + 1 == table.nRows and col + 1 == table.nColumns:
                    result.append(messages.TABLE_END)
        if result:
            result.extend(acss)
        return result

    #####################################################################
    #                                                                   #
    # Terminal information                                              #
    #                                                                   #
    #####################################################################

    def _generateTerminal(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) used especially for handling terminal objects.
        This either is the name of the frame the terminal is in or the
        displayed label of the terminal.  [[[WDW - it might be nice
        to return an empty array if this is not a terminal.]]]
        """
        result = []
        acss = self.voice(DEFAULT)
        title = None
        frame = self._script.utilities.ancestorWithRole(
            obj, [pyatspi.ROLE_FRAME], [])
        if frame:
            title = frame.name
        if not title:
            title = self._script.utilities.displayedLabel(obj)
        result.append(title)
        if result:
            result.extend(acss)
        return result

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

        result = self._generateSubstring(obj, **args)
        if result:
            return result

        acss = self.voice(DEFAULT)
        result = generator.Generator._generateCurrentLineText(self, obj, **args)
        if result:
            if result == ["\n"]:
                result = [messages.BLANK]
            result.extend(acss)
        return result

    def _generateDisplayedText(self, obj, **args):
        result = self._generateSubstring(obj, **args)
        if result:
            return result

        acss = self.voice(DEFAULT)
        result = generator.Generator._generateDisplayedText(self, obj, **args)
        if result:
            string = result[0].strip()
            if len(string) == 1 and self._script.utilities.isMath(obj):
                charname = chnames.getCharacterName(string)
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
                if char[0] == "\n" and startOffset == caretOffset \
                       and _settingsManager.getSetting('speakBlankLines'):
                    textContents = (messages.BLANK)

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
        return result

    def generateTextIndentation(self, obj, **args):
        return self._generateTextIndentation(obj, **args)

    def _generateTextIndentation(self, obj, **args):
        """Speaks a summary of the number of spaces and/or tabs at the
        beginning of the given line.

        Arguments:
        - obj: the text object.
        - line: the string to check for spaces and tabs.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        acss = self.voice(SYSTEM)
        if not _settingsManager.getSetting('enableSpeechIndentation'):
            return []
        line =  args.get('alreadyFocused', "")
        if not line:
            [line, caretOffset, startOffset] = \
              self._script.getTextLineAtCaret(obj)

        # For the purpose of speaking the text indentation, replace
        # occurances the non breaking space character with spaces.
        line = line.replace("\u00a0", " ")
        spaceCount = 0
        tabCount = 0
        utterance = ""
        offset = 0
        while True:
            while (offset < len(line)) and line[offset] == ' ':
                spaceCount += 1
                offset += 1
            if spaceCount:
                utterance += "%s " % messages.spacesCount(spaceCount)
            while (offset < len(line)) and line[offset] == '\t':
                tabCount += 1
                offset += 1
            if tabCount:
                utterance += "%s " % messages.tabsCount(tabCount)
            if not (spaceCount  or tabCount):
                break
            spaceCount  = tabCount = 0

        result = [utterance]
        if result and result[0]:
            result.extend(acss)
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

        result = []
        acss = self.voice(SYSTEM)
        try:
            value = obj.queryValue()
        except NotImplementedError:
            pass
        else:
            percentValue = \
                (value.currentValue
                 / (value.maximumValue - value.minimumValue)) \
                * 100.0
            result.append(messages.percentage(percentValue))
        if result:
            result.extend(acss)
        return result

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
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(SYSTEM)
        childNodes = self._script.utilities.childNodes(obj)
        children = len(childNodes)
        if children:
            result.append(messages.itemCount(children))
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

        items = self._script.utilities.selectedChildren(obj)
        items = items or [self._script.utilities.focusedChild(obj)]
        if not (items and items[0]):
            return result

        items = list(map(self._generateName, items))
        for item in items:
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
        priorObj = args.get('priorObj', None)
        commonAncestor = self._script.utilities.commonAncestor(priorObj, obj)
        try:
            role = commonAncestor.getRole()
        except:
            pass
        else:
            if role == pyatspi.ROLE_COMBO_BOX:
                return []

        skipRoles = args.get('skipRoles', [])
        stopAtRoles = args.get('stopAtRoles', [])
        stopAtRoles.append(pyatspi.ROLE_APPLICATION)
        if obj != commonAncestor:
            parent = obj.parent
            while parent and not parent in [commonAncestor, parent.parent]:
                parentRole = parent.getRole()
                if parentRole in stopAtRoles:
                    break
                if parentRole not in skipRoles \
                   and not self._script.utilities.isLayoutOnly(parent):
                    result.append(self.generate(parent, formatType='focused'))
                parent = parent.parent
        result.reverse()
        return result

    def _generateOldAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object being left."""

        return []

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

        # TODO - JD: This is not the right way to do this, but we can fix
        # that as part of the removal of formatting strings.
        start = args.get('startOffset')
        end = args.get('endOffset')
        if start is not None or end is not None:
            return []

        result = []
        priorObj = args.get('priorObj')
        if obj.getRole() == pyatspi.ROLE_MENU_ITEM \
           and (not priorObj or priorObj.getRole() == pyatspi.ROLE_WINDOW):
            return result

        topLevelObj = self._script.utilities.topLevelObject(obj)
        if priorObj \
           or (topLevelObj and topLevelObj.getRole() == pyatspi.ROLE_DIALOG):
            result = self._generateAncestors(obj, **args)
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

        if obj.getRole() == pyatspi.ROLE_MENU \
           and obj.parent == self._script.utilities.topLevelObject(obj):
            return []

        result = []
        acss = self.voice(SYSTEM)
        position, total = self._script.utilities.getPositionAndSetSize(obj)
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
            childResult = self._generateName(child)
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
            result.append(self._generateLabelAndName(frame))
        if dialog:
            result.append(self._generateLabelAndName(dialog))
        alertAndDialogCount = \
                    self._script.utilities.unfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            dialogs = [messages.dialogCountSpeech(alertAndDialogCount)]
            dialogs.extend(acss)
            result.append(dialogs)
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

    def _getAlternativeRole(self, obj, **args):
        if self._script.utilities.isMath(obj):
            if self._script.utilities.isMathFraction(obj):
                return 'ROLE_MATH_FRACTION'
            if self._script.utilities.isMathRoot(obj):
                return 'ROLE_MATH_ROOT'
            if self._script.utilities.isMathSubOrSuperScript(obj):
                return 'ROLE_MATH_SCRIPT_SUBSUPER'
            if self._script.utilities.isMathUnderOrOverScript(obj):
                return 'ROLE_MATH_SCRIPT_UNDEROVER'
            if self._script.utilities.isMathMultiScript(obj):
                return 'ROLE_MATH_MULTISCRIPT'
            if self._script.utilities.isMathEnclose(obj):
                return 'ROLE_MATH_ENCLOSED'
            if self._script.utilities.isMathFenced(obj):
                return 'ROLE_MATH_FENCED'
            if self._script.utilities.isMathTable(obj):
                return 'ROLE_MATH_TABLE'
            if self._script.utilities.isMathTableRow(obj):
                return 'ROLE_MATH_TABLE_ROW'
        if self._script.utilities.isStatic(obj):
            return 'ROLE_STATIC'

        return args.get('role', obj.getRole())

    def _generatePause(self, obj, **args):
        if not _settingsManager.getSetting('enablePauseBreaks') \
           or args.get('eliminatePauses', False):
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
        rv = voices.get(voicename)
        if not rv or rv.get('established') == False:
            rv = voices.get(voiceType.get(DEFAULT))

        return [acss.ACSS(rv)]
