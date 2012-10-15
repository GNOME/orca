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
import urlparse, urllib2
from gi.repository import Atspi, Atk

from . import debug
from . import generator
from . import settings
from . import settings_manager
from . import sound
from . import text_attribute_names

from .orca_i18n import _
from .orca_i18n import ngettext
from .orca_i18n import C_

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

    def _addGlobals(self, globalsDict):
        """Other things to make available from the formatting string.
        """
        generator.Generator._addGlobals(self, globalsDict)
        globalsDict['voice'] = self.voice
        globalsDict['play'] = self.play

    def play(self, key):
        """Returns an array containing a sound.Sound instance.
        The key can a value to be used to look up a filename in the
        settings.py:sounds dictionary (e.g., a pyatspi.ROLE_* value)
        or just the name of an audio file to use.
        """
        sounds = _settingsManager.getSetting('sounds')
        try:
            soundBite = sound.Sound(sounds[key])
        except:
            if isinstance(key, basestring):
                soundBite = sound.Sound(key)
            else:
                soundBite = None
        return [soundBite]

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
            if obj.name and (len(obj.name)):
                result.append(obj.name)
                result.extend(acss)
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

        result = []
        acss = self.voice(SYSTEM)
        role = args.get('role', obj.getRole())
        if (role != pyatspi.ROLE_UNKNOWN):
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

    @staticmethod
    def getLocalizedRoleName(obj, role=None):
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
        labels = self._script.utilities.unrelatedLabels(obj)
        for label in labels:
            name = self._generateName(label, **args)
            result.extend(name)
        if result:
            result.extend(acss)
        return result

    def _generateEmbedded(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) used especially for handling embedded objects.
        This either is the label or name of the object or the name of
        the application for the object.
        """
        acss = self.voice(DEFAULT)
        result = self._generateLabelOrName(obj, **args)
        if not result:
            try:
                result.append(obj.getApplication().name)
            except:
                pass
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
        if obj.getState().contains(pyatspi.STATE_MULTISELECTABLE):
            # Translators: "multi-select" refers to a web form list
            # in which more than one item can be selected at a time.
            #
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
            link_uri_info = urlparse.urlparse(link_uri)
            if link_uri_info[0] in ["ftp", "ftps", "file"]:
                fileName = link_uri_info[2].split('/')
                # Translators: this refers to a link to a file, where
                # the first item is the protocol (ftp, ftps, or file)
                # and the second item the name of the file being linked
                # to.
                #
                result.append(_("%(uri)s link to %(file)s") \
                              % {"uri" : link_uri_info[0],
                                 "file" : fileName[-1]})
            else:
                # Translators: this is the protocol of a link eg. http, mailto.
                #
                linkOutput = _("%s link") % link_uri_info[0]
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
            link_uri_info = urlparse.urlparse(link_uri)
        else:
            return result
        doc_uri = self._script.utilities.documentFrameURI()
        if doc_uri:
            doc_uri_info = urlparse.urlparse(doc_uri)
            if link_uri_info[1] == doc_uri_info[1]:
                if link_uri_info[2] == doc_uri_info[2]:
                    # Translators: this is an indication that a given
                    # link points to an object that is on the same page.
                    #
                    result.append(_("same page"))
                else:
                    # Translators: this is an indication that a given
                    # link points to an object that is at the same site
                    # (but not on the same page as the link).
                    #
                    result.append(_("same site"))
            else:
                # check for different machine name on same site
                #
                linkdomain = link_uri_info[1].split('.')
                docdomain = doc_uri_info[1].split('.')
                if len(linkdomain) > 1 and docdomain > 1  \
                    and linkdomain[-1] == docdomain[-1]  \
                    and linkdomain[-2] == docdomain[-2]:
                    # Translators: this is an indication that a given
                    # link points to an object that is at the same site
                    # (but not on the same page) as the link.
                    #
                    result.append(_("same site"))
                else:
                    # Translators: this is an indication that a given
                    # link points to an object that is at a different
                    # site than that of the link.
                    #
                    result.append(_("different site"))
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
            x = urllib2.urlopen(uri)
            try:
                sizeString = x.info()['Content-length']
            except KeyError:
                pass
        except (ValueError, urllib2.URLError, OSError):
            pass
        if sizeString:
            size = int(sizeString)
            if size < 10000:
                # Translators: This is the size of a file in bytes
                #
                result.append(ngettext("%d byte", "%d bytes", size) % size)
            elif size < 1000000:
                # Translators: This is the size of a file in kilobytes
                #
                result.append(_("%.2f kilobytes") % (float(size) * .001))
            elif size >= 1000000:
                # Translators: This is the size of a file in megabytes
                #
                result.append(_("%.2f megabytes") % (float(size) * .000001))
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
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            result.append(_("blank"))
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

        result = []
        acss = self.voice(STATE)
        # If this is an icon within an layered pane or a table cell
        # within a table or a tree table and the item is focused but not
        # selected, let the user know. See bug #486908 for more details.
        #
        checkIfSelected = False
        objRole, parentRole, state = None, None, None
        if obj:
            objRole = obj.getRole()
            state = obj.getState()
            if obj.parent:
                parentRole = obj.parent.getRole()

        if objRole == pyatspi.ROLE_TABLE_CELL \
           and (parentRole == pyatspi.ROLE_TREE_TABLE \
                or parentRole == pyatspi.ROLE_TABLE):
            checkIfSelected = True

        # If we met the last set of conditions, but we got here by
        # moving left or right on the same row, then don't announce the
        # selection state to the user. See bug #523235 for more details.
        #
        lastKey, mods = self._script.utilities.lastKeyAndModifiers()
        if checkIfSelected and lastKey in ["Left", "Right"]:
            checkIfSelected = False

        if objRole == pyatspi.ROLE_ICON \
           and parentRole == pyatspi.ROLE_LAYERED_PANE:
            checkIfSelected = True

        if checkIfSelected \
           and state and not state.contains(pyatspi.STATE_SELECTED):
            # Translators: this is in reference to a table cell being
            # selected or not.
            #
            result.append(C_("tablecell", "not selected"))
            result.extend(acss)

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
            # Translators: this is in references to a column in a
            # table.
            result.append(_("column %d") % (col + 1))
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
            # Translators: this is in references to a row in a table.
            #
            result.append(_("row %d") % (row + 1))
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
            # Translators: this is in references to a column in a
            # table.
            result.append(_("column %(index)d of %(total)d") \
                          % {"index" : (col + 1),
                             "total" : table.nColumns})
            # Translators: this is in reference to a row in a table.
            #
            result.append(_("row %(index)d of %(total)d") \
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
                    # Translators: This is to indicate to the user that
                    # he/she is in the last cell of a table in a document.
                    #
                    result.append(_("End of table"))
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
        acss = self.voice(DEFAULT)
        result = generator.Generator._generateCurrentLineText(self, obj, **args)
        if result:
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
                localizedKey = text_attribute_names.getTextAttributeName(key)
                if key in attributesDictionary:
                    attribute = attributesDictionary[key]
                    localizedValue = \
                        text_attribute_names.getTextAttributeName(attribute)
                    if attribute:
                        # If it's the 'weight' attribute and greater than 400,
                        # just speak it as bold, otherwise speak the weight.
                        #
                        if key == "weight":
                            if int(attribute) > 400:
                                attribStr += " "
                                # Translators: bold as in the font sense.
                                #
                                attribStr += _("bold")
                        elif key == "underline":
                            if attribute != "none":
                                attribStr += " "
                                attribStr += localizedKey
                        elif key == "style":
                            if attribute != "normal":
                                attribStr += " "
                                attribStr += localizedValue
                        else:
                            attribStr += " "
                            attribStr += (localizedKey + " " + localizedValue)

            # Also check to see if this is a hypertext link.
            #
            if self._script.utilities.linkIndex(obj, textOffset) >= 0:
                attribStr += " "
                # Translators: this indicates that this piece of
                # text is a hypertext link.
                #
                attribStr += _("link")

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
        textContents = ""
        selected = False

        nSelections = textObj.getNSelections()

        [current, other] = self._script.utilities.hasTextSelections(obj)
        if current or other:
            selected = True
            [textContents, startOffset, endOffset] = \
                self._script.utilities.allSelectedText(obj)
        else:
            # Get the line containing the caret
            #
            [line, startOffset, endOffset] = textObj.getTextAtOffset(
                textObj.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            if len(line):
                # Check for embedded object characters. If we find any,
                # expand the text. TODO - JD: This expansion doesn't
                # include the role information; just the text. However,
                # the handling of roles should probably be dealt with as
                # a formatting string. We have not yet worked out how to
                # do this with Gecko (primary user of embedded object
                # characters). Until we do, this expansion is better than
                # presenting the actual embedded object character.
                #
                unicodeText = line.decode("UTF-8")
                if self._script.EMBEDDED_OBJECT_CHARACTER in unicodeText:
                    line = self._script.utilities.expandEOCs(
                        obj, startOffset, endOffset)
                line = self._script.utilities.adjustForRepeats(line)
                textContents = line
            else:
                char = textObj.getTextAtOffset(caretOffset,
                    pyatspi.TEXT_BOUNDARY_CHAR)
                if char[0] == "\n" and startOffset == caretOffset \
                       and _settingsManager.getSetting('speakBlankLines'):
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    textContents = (_("blank"))

        self._script.generatorCache['textInformation'] = \
            [textContents, startOffset, endOffset, selected]

        return self._script.generatorCache['textInformation']

    def _generateTextContent(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the text content.  This requires
        _generateTextInformation to have been called prior to this method.
        """
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

        result = []
        acss = self.voice(SYSTEM)

        [line, startOffset, endOffset, selected] = \
            self._getTextInformation(obj)

        if selected:
            # Translators: when the user selects (highlights) text in
            # a document, Orca lets them know this.
            #
            text = C_("text", "selected")
            result.append(text)
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
                    # Translators: when the user selects (highlights) text in
                    # a document, Orca lets them know this.
                    #
                    result = [C_("text", "selected")]
                    result.extend(acss)
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
        # occurances of UTF-8 '\302\240' (non breaking space) with
        # spaces.
        #
        line = line.replace("\302\240",  " ")
        line = line.decode("UTF-8")

        spaceCount = 0
        tabCount = 0
        utterance = ""
        offset = 0
        while True:
            while (offset < len(line)) and line[offset] == ' ':
                spaceCount += 1
                offset += 1
            if spaceCount:
                # Translators: this is the number of space characters on a line
                # of text.
                #
                utterance += ngettext("%d space",
                                      "%d spaces",
                                      spaceCount) % spaceCount + " "

            while (offset < len(line)) and line[offset] == '\t':
                tabCount += 1
                offset += 1
            if tabCount:
                # Translators: this is the number of tab characters on a line
                # of text.
                #
                utterance += ngettext("%d tab",
                                      "%d tabs",
                                      tabCount) % tabCount + " "

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
            # Translators: this is the percentage value of a progress bar.
            #
            percentage = ngettext("%d percent",
                                  "%d percent",
                                  percentValue) % percentValue
            result.append(percentage)
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
            # Translators: this is the number of items in a layered
            # pane or table.
            #
            itemString = ngettext("%d item", "%d items", children) % children
            result.append(itemString)
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
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            result.append(_("0 items"))
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
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            result.append(_("0 items"))
            result.extend(acss)
        return result

    def _generateFocusedItem(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role != pyatspi.ROLE_LIST:
            return result

        try:
            s = obj.querySelection()
        except NotImplementedError:
            isFocused = \
                lambda x: x and x.getState().contains(pyatspi.STATE_FOCUSED)
            items = pyatspi.utils.findAllDescendants(obj, isFocused)
        else:
            items = [s.getSelectedChild(i) for i in range(s.nSelectedChildren)]
            if not items and obj.childCount:
                items.append(obj[0])

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

        result = []
        acss = self.voice(SYSTEM)
        # TODO - JD: Is there a better way to do this other than
        # hard-coding it in?
        #
        if args.get('role', obj.getRole()) \
                in [pyatspi.ROLE_ICON, pyatspi.ROLE_CANVAS]:
            obj = obj.parent
        childCount = obj.childCount
        selectedItems = []
        totalSelectedItems = 0
        currentItem = 0
        for child in obj:
            state = child.getState()
            if state.contains(pyatspi.STATE_SELECTED):
                totalSelectedItems += 1
                selectedItems.append(child)
            if state.contains(pyatspi.STATE_FOCUSED):
                currentItem = child.getIndexInParent() + 1
        # Translators: this is a count of the number of selected icons
        # and the count of the total number of icons within an icon panel.
        # An example of an icon panel is the Nautilus folder view.
        #
        countString = ngettext("%(index)d of %(total)d item selected",
                               "%(index)d of %(total)d items selected",
                               childCount) \
                      % {"index" : totalSelectedItems,
                         "total" : childCount}
        result.append(countString)
        result.extend(acss)
        result.append(self._script.formatting.getString(
                          mode='speech',
                          stringType='iconindex') \
                      % {"index" : currentItem,
                         "total" : childCount})
        result.extend(acss)
        return result

    def _generateSelectedItems(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the names of all the selected items.
        This object will be an icon panel or a layered pane.
        """
        result = []
        # TODO - JD: Is there a better way to do this other than
        # hard-coding it in?
        #
        if args.get('role', obj.getRole()) == pyatspi.ROLE_ICON:
            obj = obj.parent
        for child in obj:
            if child.getState().contains(pyatspi.STATE_SELECTED):
                result.extend(self._generateLabelAndName(child))
        return result

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
            # Translators: this tells the user how many unfocused
            # alert and dialog windows that this application has.
            #
            result.append(ngettext("%d unfocused dialog",
                            "%d unfocused dialogs",
                            alertAndDialogCount) % alertAndDialogCount)
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
        acss = self.voice(DEFAULT)
        priorObj = args.get('priorObj', None)
        requireText = args.get('requireText', True)
        commonAncestor = self._script.utilities.commonAncestor(priorObj, obj)
        if obj != commonAncestor:
            parent = obj.parent
            if parent \
                and (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                and (parent.getRole() == pyatspi.ROLE_TABLE_CELL):
                parent = parent.parent
            while parent and (parent.parent != parent):
                if parent == commonAncestor:
                    break
                if not self._script.utilities.isLayoutOnly(parent):
                    text = self._script.utilities.displayedLabel(parent)
                    if not text \
                       and (not requireText \
                            or (requireText \
                                and 'Text' in pyatspi.listInterfaces(parent))):
                        text = self._script.utilities.displayedText(parent)
                    try:
                        pRole = parent.getRole()
                    except:
                        pRole = None
                    if not text \
                       and pRole in [pyatspi.ROLE_MENU, pyatspi.ROLE_PAGE_TAB]:
                        text = parent.name
                    if text and len(text.strip()):
                        roleInfo = self._generateRoleName(parent)
                        if roleInfo:
                            roleInfo.reverse()
                        # Push announcement of cell to the end
                        #
                        if pRole not in \
                               [pyatspi.ROLE_TABLE_CELL, pyatspi.ROLE_FILLER]:
                            result.extend(roleInfo)
                        result.extend(acss)
                        result.append(text)
                        if pRole == pyatspi.ROLE_TABLE_CELL:
                            result.extend(roleInfo)
                parent = parent.parent
        result.reverse()
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
        result = []
        if args.get('priorObj', None):
            result = self._generateAncestors(obj, **args)
        return result

    def _generateParentRoleName(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the role name of the parent of obj.
        """
        if args.get('role', obj.getRole()) == pyatspi.ROLE_ICON \
           and args.get('formatType', None) \
               in ['basicWhereAmI', 'detailedWhereAmI']:
            # Translators: this is an alternative name for the
            # parent object of a series of icons.
            #
            return [_("Icon panel")]
        elif obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
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

        result = []
        acss = self.voice(SYSTEM)
        position = -1
        index = 0
        total = 0
        name = self._generateName(obj)
        # TODO - JD: There might be a better way to do this (e.g. pass
        # roles in maybe?).
        #
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_COMBO_BOX:
            obj = obj[0]
        elif role in [pyatspi.ROLE_PAGE_TAB,
                      pyatspi.ROLE_MENU,
                      pyatspi.ROLE_MENU_ITEM,
                      pyatspi.ROLE_CHECK_MENU_ITEM,
                      pyatspi.ROLE_RADIO_MENU_ITEM]:
            obj = obj.parent
        elif role == pyatspi.ROLE_LIST_ITEM:
            parent = obj.parent
            for relation in obj.getRelationSet():
                if relation.getRelationType() == \
                        pyatspi.RELATION_NODE_CHILD_OF:
                    # childNodes assumes that we have an accessible table
                    # interface to work with. If we don't, it will fail. So
                    # don't set the parent until verifying the interface we
                    # expect actually exists.
                    #
                    target = relation.getTarget(0)
                    try:
                        target.parent.queryTable()
                    except:
                        pass
                    else:
                        parent = target
                    break
            obj = parent
        else:
            obj = obj.parent

        # We want to return the position relative to this hierarchical
        # level and not the entire list.  If the object in question
        # uses the NODE_CHILD_OF relationship, we need to use it instead
        # of the childCount.
        #
        childNodes = self._script.utilities.childNodes(obj)
        total = len(childNodes)
        for i in range(0, total):
            childName = self._generateName(childNodes[i])
            if childName == name:
                position = i+1
                break

        if not total:
            for child in obj:
                nextName = self._generateName(child)
                state = child.getState()
                if not nextName or nextName[0] in ["", "Empty", "separator"] \
                   or not state.contains(pyatspi.STATE_VISIBLE):
                    continue

                index += 1
                total += 1

                if nextName == name:
                    position = index

        if (_settingsManager.getSetting('enablePositionSpeaking') \
             or args.get('forceList', False)) \
           and position >= 0:
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
                # Translators: The "default" button in a dialog box is the
                # button that gets activated when Enter is pressed anywhere
                # within that dialog box.
                #
                result.append(_("Default button is %s") % name[0])
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
        result = []
        statusBar = self._script.utilities.statusBar(obj)
        if statusBar:
            name = self._generateName(statusBar)
            if name:
                result.extend(name)
            else:
                for child in statusBar:
                    result.extend(self._generateName(child))
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
            # Translators: this tells the user how many unfocused
            # alert and dialog windows that this application has.
            #
            dialogs = []
            dialogs.append(ngettext("%d unfocused dialog",
                                    "%d unfocused dialogs",
                                    alertAndDialogCount) % alertAndDialogCount)
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
        result.extend(self._script.tutorialGenerator.getTutorial(
                obj,
                alreadyFocused,
                forceTutorial))
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

    #####################################################################
    #                                                                   #
    # Other things for prosody and voice selection                      #
    #                                                                   #
    #####################################################################

    def _generatePause(self, obj, **args):
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
        if rv and rv.get('established') == False:
            rv.pop('established')

        return [rv]
