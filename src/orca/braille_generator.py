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

"""Utilities for obtaining braille presentations for objects."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
from gi.repository import Atspi, Atk

from . import braille
from . import debug
from . import generator
from . import messages
from . import object_properties
from . import orca_state
from . import settings
from . import settings_manager
from .braille_rolenames import shortRoleNames

_settingsManager = settings_manager.getManager()

class Space:
    """A dummy class to indicate we want to insert a space into an
    utterance, but only if there is text prior to the space."""
    def __init__(self, delimiter=" "):
        self.delimiter = delimiter

SPACE = [Space()]

class BrailleGenerator(generator.Generator):
    """Takes accessible objects and produces a list of braille Regions
    for those objects.  See the generateBraille method, which is the
    primary entry point.  Subclasses can feel free to override/extend
    the brailleGenerators instance field as they see fit."""

    SKIP_CONTEXT_ROLES = (pyatspi.ROLE_MENU,
                          pyatspi.ROLE_MENU_BAR,
                          pyatspi.ROLE_PAGE_TAB_LIST,
                          pyatspi.ROLE_COMBO_BOX)

    def __init__(self, script):
        generator.Generator.__init__(self, script, "braille")

    def _addGlobals(self, globalsDict):
        """Other things to make available from the formatting string.
        """
        generator.Generator._addGlobals(self, globalsDict)
        globalsDict['space'] = self.space
        globalsDict['Component'] = braille.Component
        globalsDict['Region'] = braille.Region
        globalsDict['Text'] = braille.Text
        globalsDict['Link'] = braille.Link
        globalsDict['asString'] = self.asString

    def generateBraille(self, obj, **args):
        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: generation disabled")
            return [[], None]

        if obj == orca_state.locusOfFocus \
           and not args.get('formatType', None):
            args['formatType'] = 'focused'
        result = self.generate(obj, **args)

        # We guess at the focused region.  It's going to be a
        # Component or Text region whose accessible is the same
        # as the object we're generating braille for.  There is
        # a small hack-like thing here where we include knowledge
        # that we represent the text area of editable comboboxes
        # instead of the combobox itself.  We also do the same
        # for table cells because they sometimes have children
        # that we present.
        #
        try:
            focusedRegion = result[0]
        except:
            focusedRegion = None
        for region in result:
            try:
                role = obj.getRole()
            except:
                role = None
            if isinstance(region, (braille.Component, braille.Text)) \
               and region.accessible == obj:
                focusedRegion = region
                break
            elif isinstance(region, braille.Text) \
                 and role == pyatspi.ROLE_COMBO_BOX \
                 and region.accessible.parent == obj:
                focusedRegion = region
                break
            elif isinstance(region, braille.Component) \
                 and role == pyatspi.ROLE_TABLE_CELL \
                 and region.accessible.parent == obj:
                focusedRegion = region
                break

        return [result, focusedRegion]

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _generateRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings, with
        the exception that the pyatspi.ROLE_UNKNOWN role will yield an
        empty array.  Note that a 'role' attribute in args will
        override the accessible role of the obj.
        """
        result = []
        role = args.get('role', obj.getRole())
        verbosityLevel = _settingsManager.getSetting('brailleVerbosityLevel')

        doNotPresent = [pyatspi.ROLE_UNKNOWN,
                        pyatspi.ROLE_FILLER,
                        pyatspi.ROLE_EXTENDED,
                        pyatspi.ROLE_LINK]

        # egg-list-box, e.g. privacy panel in gnome-control-center
        if obj.parent and obj.parent.getRole() == pyatspi.ROLE_LIST_BOX:
            doNotPresent.append(obj.getRole())

        if verbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            doNotPresent.extend([pyatspi.ROLE_ICON, pyatspi.ROLE_CANVAS])

        if role == pyatspi.ROLE_HEADING:
            level = self._script.utilities.headingLevel(obj)
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)

        elif verbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
           and not args.get('readingRow', False) and role not in doNotPresent:
            result.append(self.getLocalizedRoleName(obj, role))
        return result

    def getLocalizedRoleName(self, obj, role=None):
        """Returns the localized name of the given Accessible object; the name
        is suitable to be brailled.

        Arguments:
        - obj: an Accessible object
        - role: an optional pyatspi role to use instead
        """

        if _settingsManager.getSetting('brailleRolenameStyle') \
                == settings.BRAILLE_ROLENAME_STYLE_SHORT:
            objRole = role or obj.getRole()
            rv = shortRoleNames.get(objRole)
            if rv:
                return rv

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
        result = []
        labels = self._script.utilities.unrelatedLabels(obj)
        for label in labels:
            name = self._generateName(label, **args)
            result.extend(name)

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
        [mnemonic, shortcut, accelerator] = \
            self._script.utilities.mnemonicShortcutAccelerator(obj)
        if accelerator:
            result.append("(" + accelerator + ")")
        return result

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _generateAlertAndDialogCount(self, obj,  **args):
        """Returns an array of strings that says how many alerts and dialogs
        are associated with the application for this object.  [[[WDW -
        I wonder if this string should be moved to settings.py.]]]
        """
        result = []
        try:
            alertAndDialogCount = \
                self._script.utilities.unfocusedAlertAndDialogCount(obj)
        except:
            alertAndDialogCount = 0
        if alertAndDialogCount > 0:
             result.append(messages.dialogCountBraille(alertAndDialogCount))

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
        if not _settingsManager.getSetting('enableBrailleContext'):
            return result
        args['includeContext'] = False

        # Radio button group names are treated separately from the
        # ancestors.  However, they can appear in the ancestry as a
        # labeled panel.  So, we need to exlude the first one of
        # these things we come across.  See also the
        # generator.py:_generateRadioButtonGroup method that is
        # used to find the radio button group name.
        #
        role = args.get('role', obj.getRole())
        excludeRadioButtonGroup = role == pyatspi.ROLE_RADIO_BUTTON

        parent = obj.parent
        if parent and (parent.getRole() in self.SKIP_CONTEXT_ROLES):
            parent = parent.parent
        while parent and (parent.parent != parent):
            parentResult = []
            # [[[TODO: WDW - we might want to include more things here
            # besides just those things that have labels.  For example,
            # page tab lists might be a nice thing to include. Logged
            # as bugzilla bug 319751.]]]
            #
            try:
                role = parent.getRole()
            except:
                role = None
            if role and role != pyatspi.ROLE_FILLER \
                and role != pyatspi.ROLE_SECTION \
                and role != pyatspi.ROLE_SPLIT_PANE \
                and role != pyatspi.ROLE_DESKTOP_FRAME \
                and not self._script.utilities.isLayoutOnly(parent):
                args['role'] = role
                parentResult = self.generate(parent, **args)
            # [[[TODO: HACK - we've discovered oddness in hierarchies
            # such as the gedit Edit->Preferences dialog.  In this
            # dialog, we have labeled groupings of objects.  The
            # grouping is done via a FILLER with two children - one
            # child is the overall label, and the other is the
            # container for the grouped objects.  When we detect this,
            # we add the label to the overall context.]]]
            #
            if role in [pyatspi.ROLE_FILLER, pyatspi.ROLE_PANEL]:
                label = self._script.utilities.displayedLabel(parent)
                if label and len(label) and not label.isspace():
                    if not excludeRadioButtonGroup:
                        args['role'] = parent.getRole()
                        parentResult = self.generate(parent, **args)
                    else:
                        excludeRadioButtonGroup = False
            if result and parentResult:
                result.append(braille.Region(" "))
            result.extend(parentResult)
            if role == pyatspi.ROLE_EMBEDDED:
                break

            parent = parent.parent
        result.reverse()
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

    #####################################################################
    #                                                                   #
    # Unfortunate hacks.                                                #
    #                                                                   #
    #####################################################################

    def _generateAsPageTabOrScrollPane(self, obj, **args):
        """If this scroll pane is labelled by a page tab, then return the page
        tab information for the braille context instead. Thunderbird
        folder properties is such a case. See bug #507922 for more
        details.
        """
        result = []
        try:
            relations = obj.getRelationSet()
        except:
            relations = []
        for relation in relations:
            if relation.getRelationType() ==  pyatspi.RELATION_LABELLED_BY:
                labelledBy = relation.getTarget(0)
                result.extend(self.generate(labelledBy, **args))
                break
        if not result:
            # NOTE: there is no REAL_ROLE_SCROLL_PANE in formatting.py
            # because currently fallback to the default formatting.
            # We will provide the support for someone to override this,
            # however, so we use REAL_ROLE_SCROLL_PANE here.
            #
            oldRole = self._overrideRole('REAL_ROLE_SCROLL_PANE', args)
            result.extend(self.generate(obj, **args))
            self._restoreRole(oldRole, args)
        return result

    def _generateComboBoxTextObj(self, obj, **args):
        """For a combo box, we check to see if the text is editable. If so,
        then we want to show the text attributes (such as selection --
        see bug 496846 for more details).  This will return an array
        containing a single object, which is the accessible for the
        text object. Note that this is different from the rest of the
        generators, which all return an array of strings.  Yes, this
        is a hack.
        """
        result = []
        textObj = None
        for child in obj:
            if child and child.getRole() == pyatspi.ROLE_TEXT:
                textObj = child
        if textObj and textObj.getState().contains(pyatspi.STATE_EDITABLE):
            result.append(textObj)
        return result

    def _generateIncludeContext(self, obj, **args):
        """Returns True or False to indicate whether context should be
        included or not.
        """
        # For multiline text areas, we only show the context if we
        # are on the very first line.  Otherwise, we show only the
        # line.
        #
        include = _settingsManager.getSetting('enableBrailleContext')
        if not include:
            return include
        try:
            text = obj.queryText()
        except NotImplementedError:
            text = None
        if text and (self._script.utilities.isTextArea(obj) \
                     or (obj.getRole() in [pyatspi.ROLE_LABEL])):
            try:
                [lineString, startOffset, endOffset] = text.getTextAtOffset(
                    text.caretOffset, pyatspi.TEXT_BOUNDARY_LINE_START)
            except:
                return include

            include = startOffset == 0
            if include:
                for relation in obj.getRelationSet():
                    if relation.getRelationType() \
                            == pyatspi.RELATION_FLOWS_FROM:
                        include = not self._script.utilities.\
                            isTextArea(relation.getTarget(0))
        return include

    #####################################################################
    #                                                                   #
    # Other things for spacing                                          #
    #                                                                   #
    #####################################################################

    def _generateEol(self, obj, **args):
        result = []
        if not _settingsManager.getSetting('disableBrailleEOL'):
            if not args.get('mode', None):
                args['mode'] = self._mode
            args['stringType'] = 'eol'
            result.append(self._script.formatting.getString(**args))
        return result

    def space(self, delimiter=" "):
        if delimiter == " ":
            return SPACE
        else:
            return [Space(delimiter)]

    def asString(self, content, delimiter=" "):
        combined = ""
        prior = None
        if isinstance(content, str):
            combined = content
        elif content and isinstance(content, list):
            # Strip off leading and trailing spaces.
            #
            while content and isinstance(content[0], Space):
                content = content[1:]
            while content and isinstance(content[-1], Space):
                content = content[0:-1]
            for element in content:
                if isinstance(element, Space) and prior:
                    combined += element.delimiter
                    prior = None
                else:
                    prior = self.asString(element)
                    combined = self._script.utilities.appendString(
                        combined, prior, delimiter)
        return combined
