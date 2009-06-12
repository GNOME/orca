# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Utilities for obtaining speech utterances for objects.  In general,
there probably should be a singleton instance of the SpeechGenerator
class."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import sys
import traceback
import urlparse, urllib2

import debug
import orca_state
import pyatspi
import rolenames
import settings
import text_attribute_names

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import C_        # to provide qualified translatable strings

def _formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.args
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

# [[[WDW - general note -- for all the _generate* methods, it would be great if
# we could return an empty array if we can determine the method does not
# apply to the object.  This would allow us to reduce the number of strings
# needed in formatting.py.]]]

# The prefix to use for the individual generator methods
#
METHOD_PREFIX = "_generate"

class SpeechGenerator:
    """Takes accessible objects and produces a string to speak for
    those objects.  See the generateSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speechGenerators instance field as they see fit."""

    # pylint: disable-msg=W0142

    def _overrideRole(self, newRole, args):
        """Convenience method to allow you to temporarily override the role in
        the args dictionary.  This changes the role in args ags
        returns the old role so you can pass it back to _restoreRole.
        """
        oldRole = args.get('role', None)
        args['role'] = newRole
        return oldRole

    def _restoreRole(self, oldRole, args):
        """Convenience method to restore the old role back in the args
        dictionary.  The oldRole should have been obtained from
        _overrideRole.  If oldRole is None, then the 'role' key/value
        pair will be deleted from args.
        """
        if oldRole:
            args['role'] = oldRole
        else:
            del args['role']

    def __init__(self, script):
        self._script = script
        self._methodsDict = {}
        for method in \
            filter(lambda z: callable(z),
                   map(lambda y: getattr(self, y).__get__(self, self.__class__),
                       filter(lambda x: x.startswith(METHOD_PREFIX),
                                        dir(self)))):
            name = method.__name__[len(METHOD_PREFIX):]
            name = name[0].lower() + name[1:]
            self._methodsDict[name] = method

        # Something to help us retain things we've computed while
        # generating speech so we don't need to keep recomputing them.
        #
        self._valueCache = {}

        # Verify the formatting strings are OK.  This is only
        # for verification and does not effect the function of
        # Orca at all.

        # Populate the entire globals with empty arrays
        # for the results of all the legal method names.
        #
        methods = {}
        for key in self._methodsDict.keys():
            methods[key] = []
        methods['voice'] = self.voice
        methods['obj'] = None
        methods['role'] = None
        methods['pyatspi'] = pyatspi
        for roleKey in self._script.formatting["speech"]:
            for speechKey in ["focused", "unfocused"]:
                try:
                    evalString = \
                        self._script.formatting["speech"][roleKey][speechKey]
                except:
                    continue
                else:
                    if not evalString:
                        # It's legal to have an empty string for speech.
                        #
                        continue
                    while True:
                        try:
                            eval(evalString, methods)
                            break
                        except NameError:
                            info = _formatExceptionInfo()
                            arg = info[1][0]
                            arg = arg.replace("name '", "")
                            arg = arg.replace("' is not defined", "")
                            if not self._methodsDict.has_key(arg):
                                debug.printException(debug.LEVEL_SEVERE)
                                debug.println(
                                    debug.LEVEL_SEVERE,
                                    "Unable to find function for '%s'\n" % arg)
                            methods[arg] = []
                        except:
                            debug.printException(debug.LEVEL_SEVERE)
                            debug.println(
                                debug.LEVEL_SEVERE,
                                "While processing '%s' '%s' '%s' '%s'" \
                                % (roleKey, speechKey, evalString, methods))
                            break

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _generateName(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the name of the object.  If the
        object is directly displaying any text, that text will be
        treated as the name.  Otherwise, the accessible name of the
        object will be used.  If there is no accessible name, then the
        description of the object will be used.  This method will
        return an empty array if nothing can be found.  [[[WDW - I
        wonder if we should just have _generateName, _generateDescription,
        _generateDisplayedText, etc., that don't do any fallback.  Then, we
        can allow the formatting to do the fallback (e.g.,
        'displayedText or name or description'). [[[JD to WDW - I needed
        a _generateDescription for whereAmI. :-) See below.
        """
        result = []
        name = self._script.getDisplayedText(obj)
        if name:
            result.append(name)
        elif obj.description:
            result.append(obj.description)
        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the description of the object,
        if that description is different from that of the name and
        label.
        """
        result = []
        label = self._script.getDisplayedLabel(obj)
        if obj.description and not obj.description in [obj.name, label]:
            result.append(obj.description)
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
        result = []
        role = args.get('role', obj.getRole())
        if (role != pyatspi.ROLE_UNKNOWN):
            result.append(rolenames.getSpeechForRoleName(obj, role))
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

    def _generateLabel(self, obj, **args):
        """Returns the label for an object as an array of strings (and
        possibly voice and audio specifications).  The label is
        determined by the getDisplayedLabel of the script, and an
        empty array will be returned if no label can be found.
        """
        result = []
        label = self._script.getDisplayedLabel(obj)
        if label:
            result = [label]
        return result

    def _generateLabelAndName(self, obj, **args):
        """Returns the label and the name as an array of strings (and possibly
        voice and audio specifications).  The name will only be
        present if the name is different from the label.
        """
        result = []
        label = self._generateLabel(obj, **args)
        name = self._generateName(obj, **args)
        result.extend(label)
        if not len(label):
            result.extend(name)
        elif len(name) and name[0] != label[0]:
            result.extend(name)
        return result

    def _generateLabelOrName(self, obj, **args):
        """Returns the label as an array of strings (and possibly voice
        specifications).  If the label cannot be found, the name will
        be used instead.  If the name cannot be found, an empty array
        will be returned.
        """
        result = []
        result.extend(self._generateLabel(obj, **args))
        if not result:
            if obj.name and (len(obj.name)):
                result.append(obj.name)
        return result

    def _generateUnrelatedLabels(self, obj, **args):
        """Returns, as an array of strings (and possibly voice
        specifications), all the labels which are underneath the obj's
        hierarchy and which are not in a label for or labelled by
        relation.
        """
        labels = self._script.findUnrelatedLabels(obj)
        result = []
        for label in labels:
            name = self._generateName(label, **args)
            result.extend(name)
        return result

    def _generateEmbedded(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) used especially for handling embedded objects.
        This either is the label or name of the object or the name of
        the application for the object.
        """
        result = self._generateLabelOrName(obj, **args)
        if not result:
            try:
                result.append(obj.getApplication().name)
            except:
                pass
        return result

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generateCheckedState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the checked state of the
        object.  This is typically for check boxes. [[[WDW - should we
        return an empty array if we can guarantee we know this thing
        is not checkable?]]]  [[[WDW - I wonder if we should put these
        strings in settings.py.]]]
        """
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            # Translators: this represents the state of a checkbox.
            #
            result.append(_("partially checked"))
        elif state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checkbox.
            #
            result.append(_("checked"))
        else:
            # Translators: this represents the state of a checkbox.
            #
            result.append(_("not checked"))
        return result

    def _generateCellCheckedState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the checked state of the
        object.  This is typically for check boxes that are in a
        table. An empty array will be returned if this is not a
        checkable cell.  [[[WDW - I wonder if we can roll this into
        _generateCheckedState somehow.]]]
        """
        result = []
        try:
            action = obj.queryAction()
        except NotImplementedError:
            action = None
        if action:
            for i in range(0, action.nActions):
                # Translators: this is the action name for
                # the 'toggle' action. It must be the same
                # string used in the *.po file for gail.
                #
                if action.getName(i) in ["toggle", _("toggle")]:
                    oldRole = self._overrideRole(pyatspi.ROLE_CHECK_BOX,
                                            args)
                    result.extend(self.generateSpeech(obj, **args))
                    self._restoreRole(oldRole, args)
        return result

    def _generateRadioState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the checked state of the
        object.  This is typically for check boxes. [[[WDW - should we
        return an empty array if we can guarantee we know this thing
        is not checkable?]]] [[[WDW - I wonder if we can roll this
        into _generateCheckedState somehow and provide some sort of
        settings.py string to let you specify the wording to be used
        for different roles.]]]
        """
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            result.append(C_("radiobutton", "selected"))
        else:
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            result.append(C_("radiobutton", "not selected"))
        return result

    def _generateToggleState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the checked state of the
        object.  This is typically for check boxes. [[[WDW - should we
        return an empty array if we can guarantee we know this thing
        is not checkable?]]] [[[WDW - I wonder if we can roll this
        into _generateCheckedState somehow and provide some sort of
        settings.py string to let you specify the wording to be used
        for different roles.]]]
        """
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED) \
           or state.contains(pyatspi.STATE_PRESSED):
            # Translators: the state of a toggle button.
            #
            result.append(_("pressed"))
        else:
            # Translators: the state of a toggle button.
            #
            result.append(_("not pressed"))
        return result

    def _generateExpandableState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the expanded/collapsed state of
        an object, such as a tree node. If the object is not
        expandable, an empty array will be returned.  [[[WDW - I
        wonder if these strings should be placed in settings.py.]]]
        """
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                result.append(_("expanded"))
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                result.append(_("collapsed"))
        return result

    def _generateMultiselectableState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the multiselectable state of
        the object.  This is typically for check boxes. If the object
        is not multiselectable, an empty array will be returned.
        [[[WDW - I wonder if this string should be placed in
        settings.py.]]]
        """
        result = []
        if obj.getState().contains(pyatspi.STATE_MULTISELECTABLE):
            # Translators: "multi-select" refers to a web form list
            # in which more than one item can be selected at a time.
            #
            result.append(_("multi-select"))
        return result

    def _generateMenuItemCheckedState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the checked state of the menu
        item, only if it is checked. Otherwise, and empty array will
        be returned.  [[[WDW - I wonder if we can roll this into
        _generateCheckedState somehow.]]]
        """
        result = []
        if obj.getState().contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checked menu item.
            #
            result.append(_("checked"))
        return result

    def _generateAvailability(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the
        grayed/sensitivity/availability state of the object, but only
        if it is insensitive (i.e., grayed out and inactive).
        Otherwise, and empty array will be returned.  [[[WDW - I
        wonder if we should put this string into settings.py.]]]
        """
        result = []
        if not obj.getState().contains(pyatspi.STATE_SENSITIVE):
            # Translators: this represents an item on the screen that has
            # been set insensitive (or grayed out).
            #
            result.append(_("grayed"))
        return result

    def _generateRequired(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the required state of the
        object, but only if it is required (i.e., it is in a dialog
        requesting input and the user must give it a value).
        Otherwise, and empty array will be returned.
        """
        result = []
        if obj.getState().contains(pyatspi.STATE_REQUIRED) \
           or (obj.getRole() == pyatspi.ROLE_RADIO_BUTTON \
               and obj.parent.getState().contains(pyatspi.STATE_REQUIRED)):
            result = [settings.speechRequiredStateString]
        return result

    def _generateReadOnly(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the read only state of this
        object, but only if it is read only (i.e., it is a text area
        that cannot be edited).
        """
        result = []
        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            result.append(settings.speechReadOnlyString)
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
        # Get the URI for the link of interest and parse it. The parsed
        # URI is returned as a tuple containing six components:
        # scheme://netloc/path;parameters?query#fragment.
        #
        link_uri = self._script.getURI(obj)
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
            result.append(self._script.getDisplayedText(obj))
        else:
            link_uri_info = urlparse.urlparse(link_uri)
            if link_uri_info[0] in ["ftp", "ftps", "file"]:
                fileName = link_uri_info[2].split('/')
                # Translators: this refers to a link to a file, where
                # the first item is the protocol (ftp, ftps, or file)
                # and the second item the name of the file being linked
                # to.
                #
                result.append(_('%s link to %s') %\
                               (link_uri_info[0], fileName[-1]))
            else:
                # Translators: this is the protocol of a link eg. http, mailto.
                #
                linkOutput = _('%s link') %link_uri_info[0]
                text = self._script.getDisplayedText(obj)
                if not text:
                    # If there's no text for the link, expose part of the
                    # URI to the user.
                    #
                    text = self._script.getLinkBasename(obj)
                if text:
                    linkOutput += " " + text
                result.append(linkOutput)
                if obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                    result.extend(self._generateRoleName(obj[0]))
        return result

    def _generateSiteDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that describe the site (same or different)
        pointed to by the URI of the link associated with obj.
        """
        result = []
        link_uri = self._script.getURI(obj)
        if link_uri:
            link_uri_info = urlparse.urlparse(link_uri)
        else:
            return result
        doc_uri = self._script.getDocumentFrameURI()
        if doc_uri:
            doc_uri_info = urlparse.urlparse(doc_uri)
            if link_uri_info[1] == doc_uri_info[1]:
                if link_uri_info[2] == doc_uri_info[2]:
                    # Translators: this is an indication that a given
                    # link points to an object that is on the same page.
                    #
                    result.append(_('same page'))
                else:
                    # Translators: this is an indication that a given
                    # link points to an object that is at the same site
                    # (but not on the same page as the link).
                    #
                    result.append(_('same site'))
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
                    result.append(_('same site'))
                else:
                    # Translators: this is an indication that a given
                    # link points to an object that is at a different
                    # site than that of the link.
                    #
                    result.append(_('different site'))
        return result

    def _generateFileSize(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the size (Content-length) of
        the file pointed to by the URI of the link associated with
        obj.
        """
        result = []
        sizeString = ""
        uri = self._script.getURI(obj)
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
                result.append(ngettext('%d byte', '%d bytes', size) % size)
            elif size < 1000000:
                # Translators: This is the size of a file in kilobytes
                #
                result.append(_('%.2f kilobytes') % (float(size) * .001))
            elif size >= 1000000:
                # Translators: This is the size of a file in megabytes
                #
                result.append(_('%.2f megabytes') % (float(size) * .000001))
        return result

    #####################################################################
    #                                                                   #
    # Image information                                                 #
    #                                                                   #
    #####################################################################

    def _generateImageDescription(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the description of the image on
        the object, if it exists.  Otherwise, an empty array is
        returned.
        """
        result = []
        try:
            image = obj.queryImage()
        except NotImplementedError:
            pass
        else:
            description = image.imageDescription
            if description and len(description):
                result.append(description)
        return result

    def _generateImage(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the image on the the object, if
        it exists.  Otherwise, an empty array is returned.
        """
        result = []
        try:
            image = obj.queryImage()
        except:
            pass
        else:
            role = pyatspi.ROLE_IMAGE
            result.extend(self.generateSpeech(obj, role=role))
        return result

    #####################################################################
    #                                                                   #
    # Table interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateRowHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the row header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned.
        """
        result = []
        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            index = self._script.getCellIndex(obj)
            rowIndex = table.getRowAtIndex(index)
            if rowIndex >= 0:
                # Get the header information.  In Java Swing, the
                # information is not exposed via the description
                # but is instead a header object, so we fall back
                # to that if it exists.
                #
                # [[[TODO: WDW - the more correct thing to do, I
                # think, is to look at the row header object.
                # We've been looking at the description for so
                # long, though, that we'll give the description
                # preference for now.]]]
                #
                desc = table.getRowDescription(rowIndex)
                if not desc:
                    header = table.getRowHeader(rowIndex)
                    if header:
                        desc = self._script.getDisplayedText(header)
                if desc and len(desc):
                    text = desc
                    if settings.speechVerbosityLevel \
                            == settings.VERBOSITY_LEVEL_VERBOSE \
                       and not args.get('formatType', None) \
                           in ['basicWhereAmI', 'detailedWhereAmI']:
                        text += " " \
                            + rolenames.rolenames[\
                            pyatspi.ROLE_ROW_HEADER].speech
                    result.append(text)
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
        result = []
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
                    index = self._script.getCellIndex(priorObj)
                    oldRow = table.getRowAtIndex(index)
                else:
                    oldRow = -1

                try:
                    table = obj.parent.queryTable()
                except:
                    pass
                else:
                    index = self._script.getCellIndex(obj)
                    newRow = table.getRowAtIndex(index)
                    if (newRow >= 0) \
                       and (index != newRow) \
                       and ((newRow != oldRow) \
                            or (obj.parent != priorParent)):
                        result = self._generateRowHeader(obj, **args)
        return result

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned.
        """
        result = []
        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            index = self._script.getCellIndex(obj)
            columnIndex = table.getColumnAtIndex(index)
            if columnIndex >= 0:
                # Get the header information.  In Java Swing, the
                # information is not exposed via the description
                # but is instead a header object, so we fall back
                # to that if it exists.
                #
                # [[[TODO: WDW - the more correct thing to do, I
                # think, is to look at the row header object.
                # We've been looking at the description for so
                # long, though, that we'll give the description
                # preference for now.]]]
                #
                desc = table.getColumnDescription(columnIndex)
                if not desc:
                    header = table.getColumnHeader(columnIndex)
                    if header:
                        desc = self._script.getDisplayedText(header)
                if desc and len(desc):
                    text = desc
                    if settings.speechVerbosityLevel \
                            == settings.VERBOSITY_LEVEL_VERBOSE \
                       and not args.get('formatType', None) \
                           in ['basicWhereAmI', 'detailedWhereAmI']:
                        text += " " \
                            + rolenames.rolenames[\
                            pyatspi.ROLE_COLUMN_HEADER].speech
                    result.append(text)
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
                    index = self._script.getCellIndex(priorObj)
                    oldCol = table.getColumnAtIndex(index)
                else:
                    oldCol = -1

                try:
                    table = obj.parent.queryTable()
                except:
                    pass
                else:
                    index = self._script.getCellIndex(obj)
                    newCol = table.getColumnAtIndex(index)
                    if (newCol >= 0) \
                       and (index != newCol) \
                       and ((newCol != oldCol) \
                            or (obj.parent != priorParent)):
                        result = self._generateColumnHeader(obj, **args)
        return result

    def _generateTableCell2ChildLabel(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) for the label of a toggle in a table cell that
        has a special 2 child pattern that we run into.  Otherwise, an
        empty array is returned.
        """
        result = []

        # If this table cell has 2 children and one of them has a
        # 'toggle' action and the other does not, then present this
        # as a checkbox where:
        # 1) we get the checked state from the cell with the 'toggle' action
        # 2) we get the label from the other cell.
        # See Orca bug #376015 for more details.
        #
        if obj.childCount == 2:
            cellOrder = []
            hasToggle = [False, False]
            for i, child in enumerate(obj):
                try:
                    action = child.queryAction()
                except NotImplementedError:
                    continue
                else:
                    for j in range(0, action.nActions):
                        # Translators: this is the action name for
                        # the 'toggle' action. It must be the same
                        # string used in the *.po file for gail.
                        #
                        if action.getName(j) in ["toggle", _("toggle")]:
                            hasToggle[i] = True
                            break
            if hasToggle[0] and not hasToggle[1]:
                cellOrder = [ 1, 0 ]
            elif not hasToggle[0] and hasToggle[1]:
                cellOrder = [ 0, 1 ]
            if cellOrder:
                for i in cellOrder:
                    if not hasToggle[i]:
                        result.extend(self.generateSpeech(obj[i], **args))
        return result

    def _generateTableCell2ChildToggle(self, obj, **args):
        """Returns an array of strings (and possinly voice and audio
        specifications) for the toggle value of a toggle in a table
        cell that has a special 2 child pattern that we run into.
        Otherwise, an empty array is returned.
        """
        result = []

        # If this table cell has 2 children and one of them has a
        # 'toggle' action and the other does not, then present this
        # as a checkbox where:
        # 1) we get the checked state from the cell with the 'toggle' action
        # 2) we get the label from the other cell.
        # See Orca bug #376015 for more details.
        #
        if obj.childCount == 2:
            cellOrder = []
            hasToggle = [False, False]
            for i, child in enumerate(obj):
                try:
                    action = child.queryAction()
                except NotImplementedError:
                    continue
                else:
                    for j in range(0, action.nActions):
                        # Translators: this is the action name for
                        # the 'toggle' action. It must be the same
                        # string used in the *.po file for gail.
                        #
                        if action.getName(j) in ["toggle", _("toggle")]:
                            hasToggle[i] = True
                            break

            if hasToggle[0] and not hasToggle[1]:
                cellOrder = [ 1, 0 ]
            elif not hasToggle[0] and hasToggle[1]:
                cellOrder = [ 0, 1 ]
            if cellOrder:
                for i in cellOrder:
                    if hasToggle[i]:
                        result.extend(self.generateSpeech(obj[i], **args))
        return result

    def _generateRealTableCell(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to complexity in
        the code.  This method is used to return an array of strings
        (and possibly voice and audio specifications) for a single table
        cell itself.  The string, 'blank', is added for empty cells.
        [[[WDW - I wonder if this string and whether it is used or not
        should be put in settings.py.]]]
        """
        result = []
        oldRole = self._overrideRole('REAL_ROLE_TABLE_CELL', args)
        result.extend(self.generateSpeech(obj, **args))
        self._restoreRole(oldRole, args)
        if not result and settings.speakBlankLines \
           and not args.get('readingRow', False):
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            result = [_("blank")]
        return result

    def _generateTableCellRow(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to complexity in
        the code.  This method is used to return an array of strings
        (and possibly voice and audio specifications) for an entire row
        in a table if that's what the user has requested and if the row
        has changed.  Otherwise, it will return an array for just the
        current cell.
        """
        result = []

        try:
            parentTable = obj.parent.queryTable()
        except NotImplementedError:
            parentTable = None
        isDetailedWhereAmI = args.get('formatType', None) == 'detailedWhereAmI'
        if (settings.readTableCellRow or isDetailedWhereAmI) and parentTable \
           and (not self._script.isLayoutOnly(obj.parent)):
            parent = obj.parent
            index = self._script.getCellIndex(obj)
            row = parentTable.getRowAtIndex(index)
            column = parentTable.getColumnAtIndex(index)

            # This is an indication of whether we should speak all the
            # table cells (the user has moved focus up or down a row),
            # or just the current one (focus has moved left or right in
            # the same row).
            #
            speakAll = True
            if isDetailedWhereAmI:
                if parentTable.nColumns <= 1:
                    return result
            elif "lastRow" in self._script.pointOfReference \
               and "lastColumn" in self._script.pointOfReference:
                pointOfReference = self._script.pointOfReference
                speakAll = \
                    (pointOfReference["lastRow"] != row) \
                     or ((row == 0 or row == parentTable.nRows-1) \
                     and pointOfReference["lastColumn"] == column)
            if speakAll:
                args['readingRow'] = True
                for i in range(0, parentTable.nColumns):
                    cell = parentTable.getAccessibleAt(row, i)
                    if not cell:
                        continue
                    state = cell.getState()
                    showing = state.contains(pyatspi.STATE_SHOWING)
                    if showing:
                        # If this table cell has a "toggle" action, and
                        # doesn't have any label associated with it then
                        # also speak the table column header.
                        # See Orca bug #455230 for more details.
                        #
                        label = self._script.getDisplayedText(
                            self._script.getRealActiveDescendant(cell))
                        try:
                            action = cell.queryAction()
                        except NotImplementedError:
                            action = None
                        if action and (label == None or len(label) == 0):
                            for j in range(0, action.nActions):
                                # Translators: this is the action name for
                                # the 'toggle' action. It must be the same
                                # string used in the *.po file for gail.
                                #
                                if action.getName(j) in ["toggle",
                                                         _("toggle")]:
                                    accHeader = \
                                        parentTable.getColumnHeader(i)
                                    result.append(accHeader.name)
                        result.extend(self._generateRealTableCell(cell, **args))
            else:
                result.extend(self._generateRealTableCell(obj, **args))
        else:
            result.extend(self._generateRealTableCell(obj, **args))
        return result

    def _generateUnselectedCell(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) if this is an icon within an layered pane or a
        table cell within a table or a tree table and the item is
        focused but not selected.  Otherwise, an empty array is
        returned.  [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        result = []

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
        if checkIfSelected and orca_state.lastNonModifierKeyEvent \
           and orca_state.lastNonModifierKeyEvent.event_string \
               in ["Left", "Right"]:
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

        return result

    def _generateColumn(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the column number of a cell.
        """
        result = []
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
            index = self._script.getCellIndex(obj)
            col = table.getColumnAtIndex(index)
        if col >= 0:
            # Translators: this is in references to a column in a
            # table.
            result.append(_("column %d" % (col + 1)))
        return result

    def _generateRow(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the row number of a cell.
        """
        result = []
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
            index = self._script.getCellIndex(obj)
            row = table.getRowAtIndex(index)
        if row >= 0:
            # Translators: this is in references to a row in a table.
            #
            result.append(_("row %d" % (row + 1)))
        return result

    def _generateColumnAndRow(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the position of the cell in terms
        of its column number, the total number of columns, its row,
        and the total number of rows.
        """
        result = []
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent
        try:
            table = parent.queryTable()
        except:
            table = None
        else:
            index = self._script.getCellIndex(obj)
            col = table.getColumnAtIndex(index)
            row = table.getRowAtIndex(index)
            # Translators: this is in references to a column in a
            # table.
            result.append(_("column %d of %d") % ((col + 1), table.nColumns))
            # Translators: this is in reference to a row in a table.
            #
            result.append(_("row %d of %d") % ((row + 1), table.nRows))
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
        title = None
        frame = self._script.getFrame(obj)
        if frame:
            title = frame.name
        if not title:
            title = self._script.getDisplayedLabel(obj)
        result.append(title)
        return result

    #####################################################################
    #                                                                   #
    # Text interface information                                        #
    #                                                                   #
    #####################################################################

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
        attributesDictionary = \
            self._script.attributeStringToDictionary(defaultAttributes)

        charAttributes = text.getAttributes(textOffset)
        if charAttributes[0]:
            charDict = \
                self._script.attributeStringToDictionary(charAttributes[0])
            for key in charDict.keys():
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
            if self._script.getLinkIndex(obj, textOffset) >= 0:
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

        [current, other] = self._script.hasTextSelections(obj)
        if current or other:
            selected = True
            [textContents, startOffset, endOffset] = \
                self._script.getAllSelectedText(obj)
        else:
            # Get the line containing the caret
            #
            [line, startOffset, endOffset] = textObj.getTextAtOffset(
                textObj.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            if len(line):
                line = self._script.adjustForRepeats(line)
                textContents = line
            else:
                char = textObj.getTextAtOffset(caretOffset,
                    pyatspi.TEXT_BOUNDARY_CHAR)
                if char[0] == "\n" and startOffset == caretOffset \
                       and settings.speakBlankLines:
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

        [line, startOffset, endOffset, selected] = \
            self._getTextInformation(obj)

        # The empty string seems to be messing with using 'or' in
        # formatting strings.
        #
        if line == '':
            return []
        return [line]

    def _generateTextContentWithAttributes(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the text content, obtained from the
        'textInformation' value of self._valueCache, with character
        attribute information mixed in.  This requires
        _generateTextInformation to have been called prior to this method.
        """
        try:
            text = obj.queryText()
        except NotImplementedError:
            return []

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

        return [newLine]

    def _generateCurrentLineText(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the current line of text, if
        this is a text object.  [[[WDW - consider returning an empty
        array if this is not a text object.]]]
        """
        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        return [text]

    def _generateDisplayedText(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents all the text being displayed
        by the object. [[[WDW - consider returning an empty array if
        this is not a text object.]]]
        """
        return [self._script.getDisplayedText(obj)]

    def _generateAnyTextSelection(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if any of the text for the entire
        object is selected. [[[WDW - I wonder if this string should be
        moved to settings.py.]]]
        """
        result = []

        [line, startOffset, endOffset, selected] = \
            self._getTextInformation(obj)

        if selected:
            # Translators: when the user selects (highlights) text in
            # a document, Orca lets them know this.
            #
            text = C_("text", "selected")
            result.append(text)
        return result

    def _generateAllTextSelection(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if all the text for the entire
        object is selected. [[[WDW - I wonder if this string should be
        moved to settings.py.]]]
        """
        result = []
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
        return result

    #####################################################################
    #                                                                   #
    # Tree interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateNodeLevel(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the tree node level of the
        object, or an empty array if the object is not a tree
        node. [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        result = []
        level = self._script.getNodeLevel(obj)
        if level >= 0:
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            result.append(_("tree level %d") % (level + 1))
        return result

    def _generateNewNodeLevel(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the tree node level of the
        object, or an empty array if the object is not a tree node or
        if the node level is not different from the 'priorObj'
        'priorObj' attribute of the args dictionary.  The 'priorObj'
        is typically set by Orca to be the previous object with
        focus.  [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """

        # [[[TODO: WDW - hate duplicating code from _generateNodeLevel,
        # but don't want to call it because it will make the same
        # self._script.getNodeLevel call again.]]]
        #
        result = []
        oldLevel = self._script.getNodeLevel(args.get('priorObj', None))
        newLevel = self._script.getNodeLevel(obj)
        if (oldLevel != newLevel) and (newLevel >= 0):
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            result.append(_("tree level %d") % (newLevel + 1))
        return result

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateValue(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the value of the object.  This
        is typically the numerical value, but may also be the text
        of the 'value' attribute if it exists on the object.  [[[WDW -
        we should consider returning an empty array if there is no
        value.
        """
        return [self._script.getTextForValue(obj)]

    def _generatePercentage(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the percentage value of the
        object.  This is typically for progress bars. [[[WDW - we
        should consider returning an empty array if there is no value.
        """
        result = []
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
            percentage = _("%d percent") % percentValue
            result.append(percentage)
        return result

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _generateRadioButtonGroup(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the radio button group label
        for the object, or an empty array if the object has no such
        label.
        """
        result = []
        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            radioGroupLabel = None
            relations = obj.getRelationSet()
            for relation in relations:
                if (not radioGroupLabel) \
                    and (relation.getRelationType() \
                         == pyatspi.RELATION_LABELLED_BY):
                    radioGroupLabel = relation.getTarget(0)
                    break
            if radioGroupLabel:
                result.append(self._script.getDisplayedText(radioGroupLabel))
            else:
                parent = obj.parent
                while parent and (parent.parent != parent):
                    if parent.getRole() in [pyatspi.ROLE_PANEL,
                                            pyatspi.ROLE_FILLER]:
                        label = self._generateLabelAndName(parent)
                        if label:
                            result.extend(label)
                            break
                    parent = parent.parent
        return result

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
                result.append(self._script.getDisplayedText(radioGroupLabel))
        return result

    def _generateRealActiveDescendantDisplayedText(self, obj, **args ):
        """Objects, such as tables and trees, can represent individual cells
        via a complicated nested hierarchy.  This method returns an
        array of strings (and possibly voice and audio specifications)
        that represents the text actually being painted in the cell,
        if it can be found.  Otherwise, an empty array is returned.
        """
        result = []
        text = self._script.getDisplayedText(
          self._script.getRealActiveDescendant(obj))
        if text:
            result = [text]
        return result

    def _generateNumberOfChildren(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the number of children the
        object has.  [[[WDW - can we always return an empty array if
        this doesn't apply?]]] [[[WDW - I wonder if this string should
        be moved to settings.py.]]]
        """
        result = []
        childNodes = self._script.getChildNodes(obj)
        children = len(childNodes)
        if children:
            # Translators: this is the number of items in a layered
            # pane or table.
            #
            itemString = ngettext("%d item", "%d items", children) % children
            result.append(itemString)
        return result

    def _generateNoShowingChildren(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if this object has no showing
        children (e.g., it's an empty table or list).  object has.
        [[[WDW - can we always return an empty array if this doesn't
        apply?]]] [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        result = []
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
        return result

    def _generateNoChildren(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if this object has no children at
        all (e.g., it's an empty table or list).  object has.  [[[WDW
        - can we always return an empty array if this doesn't
        apply?]]] [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        result = []
        if not obj.childCount:
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            result.append(_("0 items"))
        return result

    def _generateSelectedItemCount(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) indicating how many items are selected in this
        and the position of the current item. This object will be an icon
        panel or a layered pane.
        """
        result = []
        # TODO - JD: Is there a better way to do this other than
        # hard-coding it in?
        #
        if args.get('role', obj.getRole()) == pyatspi.ROLE_ICON:
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
        countString = ngettext("%d of %d item selected",
                              "%d of %d items selected",
                              childCount) % \
                              (totalSelectedItems, childCount)
        result.append(countString)
        # Translators: this is a indication of the focused icon and the
        # count of the total number of icons within an icon panel. An
        # example of an icon panel is the Nautilus folder view.
        #
        itemString = _("on item %d of %d") % (currentItem, childCount)
        result.append(itemString)
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
        result = []
        # If this application has more than one unfocused alert or
        # dialog window, then speak '<m> unfocused dialogs'
        # to let the user know.
        #
        alertAndDialogCount = \
            self._script.getUnfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            # Translators: this tells the user how many unfocused
            # alert and dialog windows that this application has.
            #
            result.append(ngettext("%d unfocused dialog",
                            "%d unfocused dialogs",
                            alertAndDialogCount) % alertAndDialogCount)
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
        requireText = args.get('requireText', True)
        commonAncestor = self._script.findCommonAncestor(priorObj, obj)
        if obj != commonAncestor:
            parent = obj.parent
            if parent \
                and (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                and (parent.getRole() == pyatspi.ROLE_TABLE_CELL):
                parent = parent.parent
            while parent and (parent.parent != parent):
                if parent == commonAncestor:
                    break
                if not self._script.isLayoutOnly(parent):
                    text = self._script.getDisplayedLabel(parent)
                    if not text \
                       and (not requireText \
                            or (requireText \
                                and 'Text' in pyatspi.listInterfaces(parent))):
                        text = self._script.getDisplayedText(parent)
                    if text and len(text.strip()):
                        # Push announcement of cell to the end
                        #
                        if parent.getRole() not in [pyatspi.ROLE_TABLE_CELL,
                                                    pyatspi.ROLE_FILLER]:
                            result.extend(self._generateRoleName(parent))
                        result.append(text)
                        if parent.getRole() == pyatspi.ROLE_TABLE_CELL:
                            result.extend(self._generateRoleName(parent))
                parent = parent.parent
        return result.reverse() or result

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
        ancestor = self._script.getAncestor(obj,
                                            [pyatspi.ROLE_TOOL_BAR],
                                            [pyatspi.ROLE_FRAME])
        if ancestor:
            result.extend(self._generateLabelAndName(ancestor))
            result.extend(self._generateRoleName(ancestor))
        return result

    def _generatePositionInGroup(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a group.
        """
        result = []
        position = -1
        total = -1

        relations = obj.getRelationSet()
        for relation in relations:
            if relation.getRelationType() == pyatspi.RELATION_MEMBER_OF:
                total = relation.getNTargets()
                for i in range(0, total):
                    target = relation.getTarget(i)
                    if target == obj:
                        position = total - i
                        break

        if position >= 0:
            # Translators: this is an item in a list.
            #
            result.append(_("item %d of %d") % (position, total))

        return result

    def _generatePositionInList(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a list.
        """
        result = []
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
                    # getChildNodes assumes that we have an accessible table
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

        # We want to return the position relative to this hierarchical
        # level and not the entire list.  If the object in question
        # uses the NODE_CHILD_OF relationship, we need to use it instead
        # of the childCount.
        #
        childNodes = self._script.getChildNodes(obj)
        total = len(childNodes)
        for i in range(0, total):
            childName = self._generateName(childNodes[i])
            if childName == name:
                position = i+1
                break

        if not total:
            for child in obj:
                next = self._generateName(child)
                state = child.getState()
                if not next or next[0] in ["", "Empty", "separator"] \
                   or not state.contains(pyatspi.STATE_VISIBLE):
                    continue

                index += 1
                total += 1

                if next == name:
                    position = index

        if position >= 0:
            # Translators: this is an item in a list.
            #
            result.append(_("item %d of %d") % (position, total))

        return result

    def _generateNestingLevel(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the nesting level of an object
        in a list.
        """
        result = []
        nestingLevel = 0
        parent = obj.parent
        while parent.parent.getRole() == pyatspi.ROLE_LIST:
            nestingLevel += 1
            parent = parent.parent
        if nestingLevel:
            # Translators: this represents a list item in a document.
            # The nesting level is how 'deep' the item is (e.g., a
            # level of 2 represents a list item inside a list that's
            # inside another list).
            #
            result.append(_("Nesting level %d") % nestingLevel)
        return result

    def _generateDefaultButton(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the default button in a dialog.
        This method should initially be called with a top-level window.
        """
        result = []
        button = self._script.findDefaultButton(obj)
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
        # TODO/Question - JD to WDW: Do we want to add this to the
        # formatting strings? For now, I've not done that.
        #
        return self._generateDefaultButton(obj, **args)

    def _generateStatusBar(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the status bar of a window.
        This method should initially be called with a top-level window.
        """
        result = []
        statusBar = self._script.findStatusBar(obj)
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
        # TODO/Question - JD to WDW: Do we want to add this to the
        # formatting strings? For now, I've not done that.
        #
        return self._generateStatusBar(obj, **args)

    def generateTitle(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the title of the window, obj.
        containing the object, along with information associated with
        any unfocused dialog boxes.
        """
        # TODO/Question - JD to WDW: Do we want to add this to the
        # formatting strings? For now, I've not done that.
        #
        result = []
        frame, dialog = self._script.findFrameAndDialog(obj)
        if frame:
            result.append(self._generateLabelAndName(frame))
        if dialog:
            result.append(self._generateLabelAndName(dialog))
        alertAndDialogCount = \
                    self._script.getUnfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            # Translators: this tells the user how many unfocused
            # alert and dialog windows that this application has.
            #
            result.append(ngettext("%d unfocused dialog",
                                   "%d unfocused dialogs",
                                   alertAndDialogCount) % alertAndDialogCount)
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
        result = []
        [mnemonic, shortcut, accelerator] = self._script.getKeyBinding(obj)
        if accelerator:
            # Add punctuation for better prosody.
            #
            #if result:
            #    result[-1] += "."
            result.append(accelerator)
        return result

    def _generateMnemonic(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the mnemonic for the object, or
        an empty array if no mnemonic can be found.
        """
        result = []
        if settings.enableMnemonicSpeaking or args.get('forceMnemonic', False):
            [mnemonic, shortcut, accelerator] = self._script.getKeyBinding(obj)
            if mnemonic:
                mnemonic = mnemonic[-1] # we just want a single character
            if not mnemonic and shortcut:
                mnemonic = shortcut
            if mnemonic:
                # Add punctuation for better prosody.
                #
                #if result:
                #    utterances[-1] += "."
                result = [mnemonic]
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
        result = []
        alreadyFocused = args.get('alreadyFocused', False)
        forceTutorial = args.get('forceTutorial', False)
        result.extend(self._script.tutorialGenerator.getTutorial(
                obj,
                alreadyFocused,
                forceTutorial))
        if args.get('role', obj.getRole()) == pyatspi.ROLE_ICON \
            and args.get('formatType', 'unfocused') == 'basicWhereAmI':
            frame, dialog = self._script.findFrameAndDialog(obj)
            if frame:
                result.extend(self._script.tutorialGenerator.getTutorial(
                        frame,
                        alreadyFocused,
                        forceTutorial))
        return result

    #####################################################################
    #                                                                   #
    # Tie it all together                                               #
    #                                                                   #
    #####################################################################

    def voice(self, key=None):
        """Returns an array containing a voice.  The key is a value
        to be used to look up the voice in the settings.py:voices
        dictionary.
        """
        try:
            voice = settings.voices[key]
        except:
            voice = settings.voices[settings.DEFAULT_VOICE]
        return [voice]

    def generateSpeech(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the complete speech for the
        object.  The speech to be generated depends highly upon the
        speech formatting strings in formatting.py.

        args is a dictionary that may contain any of the following:
        - alreadyFocused: if True, we're getting speech for an object
          that previously had focus
        - priorObj: if set, represents the object that had focus before
          this object
        - includeContext: boolean (default=True) which says whether
          the context for an object should be included as a prefix
          and suffix
        - role: a role to override the object's role
        - formatType: the type of formatting, such as
          'focused', 'basicWhereAmI', etc.
        - forceMnemonic: boolean (default=False) which says if we
          should ignore the settings.enableMnemonicSpeaking setting
        - forceTutorial: boolean (default=False) which says if we
          should force a tutorial to be spoken or not
        """
        result = []
        methods = {}
        methods['voice'] = self.voice
        methods['obj'] = obj
        methods['pyatspi'] = pyatspi
        methods['role'] = args.get('role', obj.getRole())

        try:
            # We sometimes want to override the role.  We'll keep the
            # role in the args dictionary as a means to let us do so.
            #
            args['role'] = methods['role']

            # We loop through the format string, catching each error
            # as we go.  Each error should always be a NameError,
            # where the name is the name of one of our generator
            # functions.  When we encounter this, we call the function
            # and get its results, placing them in the globals for the
            # the call to eval.
            #
            args['mode'] = 'speech'
            if not args.get('formatType', None):
                if args.get('alreadyFocused', False):
                    args['formatType'] = 'focused'
                else:
                    args['formatType'] = 'unfocused'

            format = self._script.formatting.getFormat(**args)

            # Add in the speech context if this is the first time
            # we've been called.
            #
            if not args.get('recursing', False):
                self._valueCache = {}
                if args.get('includeContext', True):
                    prefix = self._script.formatting.getPrefix(**args)
                    suffix = self._script.formatting.getSuffix(**args)
                    format = '%s + %s + %s' % (prefix, format, suffix)
                args['recursing'] = True
                firstTimeCalled = True
            else:
                firstTimeCalled = False

            debug.println(debug.LEVEL_ALL, "generateSpeech for %s using '%s'" \
                          % (repr(args), format))

            assert(format)
            while True:
                try:
                    result = eval(format, methods)
                    break
                except NameError:
                    result = []
                    info = _formatExceptionInfo()
                    arg = info[1][0]
                    arg = arg.replace("name '", "")
                    arg = arg.replace("' is not defined", "")
                    if not self._methodsDict.has_key(arg):
                        debug.printException(debug.LEVEL_SEVERE)
                        debug.println(
                            debug.LEVEL_SEVERE,
                            "Unable to find function for '%s'\n" % arg)
                        break
                    methods[arg] = self._methodsDict[arg](obj, **args)
                    debug.println(debug.LEVEL_ALL,
                                  "%s=%s" % (arg, repr(methods[arg])))
        except:
            debug.printException(debug.LEVEL_SEVERE)
            result = []

        debug.println(debug.LEVEL_ALL,
                      "generateSpeech generated '%s'" % repr(result))

        return result
