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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import braille
from . import debug
from . import focus_manager
from . import generator
from . import messages
from . import object_properties
from . import settings
from . import settings_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .ax_value import AXValue
from .braille_rolenames import shortRoleNames


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

    SKIP_CONTEXT_ROLES = (Atspi.Role.MENU,
                          Atspi.Role.MENU_BAR,
                          Atspi.Role.PAGE_TAB_LIST,
                          Atspi.Role.REDUNDANT_OBJECT,
                          Atspi.Role.UNKNOWN,
                          Atspi.Role.COMBO_BOX)

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

    def _isCandidateFocusedRegion(self, obj, region):
        if not isinstance(region, (braille.Component, braille.Text)):
            return False

        if not AXUtilities.have_same_role(obj, region.accessible):
            return False

        return AXObject.get_name(obj) == AXObject.get_name(region.accessible)

    def generateBraille(self, obj, **args):
        if not settings_manager.getManager().getSetting('enableBraille') \
           and not settings_manager.getManager().getSetting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE GENERATOR: generation disabled", True)
            return [[], None]

        if obj == focus_manager.getManager().get_locus_of_focus() \
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
        except Exception:
            focusedRegion = None

        for region in result:
            if isinstance(region, (braille.Component, braille.Text)) \
               and self._script.utilities.isSameObject(region.accessible, obj, True):
                focusedRegion = region
                break
            elif isinstance(region, braille.Text) \
                 and AXUtilities.is_combo_box(obj) \
                 and AXObject.get_parent(region.accessible) == obj:
                focusedRegion = region
                break
            elif isinstance(region, braille.Component) \
                 and AXUtilities.is_table_cell(obj) \
                 and AXObject.get_parent(region.accessible) == obj:
                focusedRegion = region
                break
        else:

            def pred(x):
                return self._isCandidateFocusedRegion(obj, x)

            candidates = list(filter(pred, result))
            tokens = ["BRAILLE GENERATOR: Could not determine focused region for",
                      obj, "Candidates:", candidates]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            if len(candidates) == 1:
                focusedRegion = candidates[0]

        return [result, focusedRegion]

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _generateRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings, with
        the exception that the Atspi.Role.UNKNOWN role will yield an
        empty array.  Note that a 'role' attribute in args will
        override the accessible role of the obj.
        """

        if args.get('isProgressBarUpdate') \
           and not settings_manager.getManager().getSetting('brailleProgressBarUpdates'):
            return []

        result = []
        role = args.get('role', AXObject.get_role(obj))
        verbosityLevel = settings_manager.getManager().getSetting('brailleVerbosityLevel')

        doNotPresent = [Atspi.Role.UNKNOWN,
                        Atspi.Role.REDUNDANT_OBJECT,
                        Atspi.Role.FILLER,
                        Atspi.Role.EXTENDED,
                        Atspi.Role.LINK]

        # egg-list-box, e.g. privacy panel in gnome-control-center
        if AXUtilities.is_list_box(AXObject.get_parent(obj)):
            doNotPresent.append(AXObject.get_role(obj))

        if verbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            doNotPresent.extend([Atspi.Role.ICON, Atspi.Role.CANVAS])

        if role == Atspi.Role.HEADING:
            level = self._script.utilities.headingLevel(obj)
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)

        elif verbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
           and not args.get('readingRow', False) and role not in doNotPresent:
            result.append(self.getLocalizedRoleName(obj, **args))
        return result

    def getLocalizedRoleName(self, obj, **args):
        """Returns the localized name of the given Accessible object; the name
        is suitable to be brailled.

        Arguments:
        - obj: an Accessible object
        """

        if settings_manager.getManager().getSetting('brailleRolenameStyle') \
                == settings.BRAILLE_ROLENAME_STYLE_SHORT:
            role = args.get('role', AXObject.get_role(obj))
            rv = shortRoleNames.get(role)
            if rv:
                return rv

        return super().getLocalizedRoleName(obj, **args)

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

        verbosityLevel = settings_manager.getManager().getSetting('brailleVerbosityLevel')
        if verbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            return []

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
        except Exception:
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
        if not settings_manager.getManager().getSetting('enableBrailleContext'):
            return result
        args['includeContext'] = False

        # Radio button group names are treated separately from the
        # ancestors.  However, they can appear in the ancestry as a
        # labeled panel.  So, we need to exclude the first one of
        # these things we come across.  See also the
        # generator.py:_generateRadioButtonGroup method that is
        # used to find the radio button group name.
        #
        role = args.get('role', AXObject.get_role(obj))
        excludeRadioButtonGroup = role == Atspi.Role.RADIO_BUTTON

        parent = AXObject.get_parent_checked(obj)
        if parent and (AXObject.get_role(parent) in self.SKIP_CONTEXT_ROLES):
            parent = AXObject.get_parent_checked(parent)
        while parent:
            parentResult = []
            # [[[TODO: WDW - we might want to include more things here
            # besides just those things that have labels.  For example,
            # page tab lists might be a nice thing to include. Logged
            # as bugzilla bug 319751.]]]
            #
            role = AXObject.get_role(parent)
            if role != Atspi.Role.FILLER \
                and role != Atspi.Role.INVALID \
                and role != Atspi.Role.SECTION \
                and role != Atspi.Role.SPLIT_PANE \
                and role != Atspi.Role.DESKTOP_FRAME \
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
            if role in [Atspi.Role.FILLER, Atspi.Role.PANEL]:
                label = self._script.utilities.displayedLabel(parent)
                if label and len(label) and not label.isspace():
                    if not excludeRadioButtonGroup:
                        args['role'] = AXObject.get_role(parent)
                        parentResult = self.generate(parent, **args)
                    else:
                        excludeRadioButtonGroup = False
            if result and parentResult:
                result.append(braille.Region(" "))
            result.extend(parentResult)
            if role == Atspi.Role.EMBEDDED:
                break

            parent = AXObject.get_parent_checked(parent)
        result.reverse()
        return result

    def _generateFocusedItem(self, obj, **args):
        result = []
        role = args.get('role', AXObject.get_role(obj))
        if role not in [Atspi.Role.LIST, Atspi.Role.LIST_BOX]:
            return result

        if AXObject.supports_selection(obj):
            items = self._script.utilities.selectedChildren(obj)
        else:
            items = [AXUtilities.get_focused_object(obj)]
        if not (items and items[0]):
            return result

        for item in map(self._generateName, items):
            result.extend(item)

        return result

    def _generateTermValueCount(self, obj, **args):
        count = self._script.utilities.getValueCountForTerm(obj)
        if count < 0:
            return []

        return [f"({messages.valueCountForTerm(count)})"]

    def _generateStatusBar(self, obj, **args):
        if not AXUtilities.is_status_bar(obj):
            return []

        items = self._script.utilities.statusBarItems(obj)
        if not items or items == [obj]:
            return []

        result = []
        for child in items:
            childResult = self.generate(child, includeContext=False)
            if childResult:
                result.extend(childResult)
                result.append(braille.Region(" "))

        return result

    def _generateListBoxItemWidgets(self, obj, **args):
        if not AXUtilities.is_list_box(AXObject.get_parent(obj)):
            return []

        result = []
        for widget in AXUtilities.get_all_widgets(obj):
            result.extend(self.generate(widget, includeContext=False))
            result.append(braille.Region(" "))
        return result

    def _generateProgressBarIndex(self, obj, **args):
        if not args.get('isProgressBarUpdate') \
           or not self._shouldPresentProgressBarUpdate(obj, **args):
            return []

        acc, updateTime, updateValue = self._getMostRecentProgressBarUpdate()
        if acc != obj:
            number, count = self.getProgressBarNumberAndCount(obj)
            return [f'{number}']

        return []

    def _generateProgressBarValue(self, obj, **args):
        if args.get('isProgressBarUpdate') \
           and not self._shouldPresentProgressBarUpdate(obj, **args):
            return []

        result = self._generatePercentage(obj, **args)
        if obj == focus_manager.getManager().get_locus_of_focus() and not result:
            return ['']

        return result

    def _generatePercentage(self, obj, **args):
        percent = AXValue.get_value_as_percent(obj)
        if percent is not None:
            return [f'{percent}%']

        return []

    def _getProgressBarUpdateInterval(self):
        interval = settings_manager.getManager().getSetting('progressBarBrailleInterval')
        if interval is None:
            return super()._getProgressBarUpdateInterval()

        return int(interval)

    def _shouldPresentProgressBarUpdate(self, obj, **args):
        if not settings_manager.getManager().getSetting('brailleProgressBarUpdates'):
            return False

        return super()._shouldPresentProgressBarUpdate(obj, **args)

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
        labels = self._script.utilities.labelsForObject(obj)
        for label in labels:
            result.extend(self.generate(label, **args))
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

    def _generateIncludeContext(self, obj, **args):
        """Returns True or False to indicate whether context should be
        included or not.
        """

        if args.get('isProgressBarUpdate'):
            return False

        # For multiline text areas, we only show the context if we
        # are on the very first line.  Otherwise, we show only the
        # line.
        #
        include = settings_manager.getManager().getSetting('enableBrailleContext')
        if not include:
            return include
        try:
            text = obj.queryText()
        except NotImplementedError:
            text = None
        if text and (self._script.utilities.isTextArea(obj) or AXUtilities.is_label(obj)):
            try:
                [lineString, startOffset, endOffset] = text.getTextAtOffset(
                    text.caretOffset, Atspi.TextBoundaryType.LINE_START)
            except Exception:
                return include

            include = startOffset == 0
            if include:
                relation = AXObject.get_relation(obj, Atspi.RelationType.FLOWS_FROM)
                if relation:
                    include = not self._script.utilities.isTextArea(relation.get_target(0))
        return include

    #####################################################################
    #                                                                   #
    # Other things for spacing                                          #
    #                                                                   #
    #####################################################################

    def _generateEol(self, obj, **args):
        result = []
        if not settings_manager.getManager().getSetting('disableBrailleEOL'):
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
