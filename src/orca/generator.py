# Orca
#
# Copyright 2009 Sun Microsystems Inc.
# Copyright 2015-2016 Igalia, S.L.
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

"""Superclass of classes used to generate presentations for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2009 Sun Microsystems Inc." \
                "Copyright (c) 2015-2016 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

gi.require_version('Atk', '1.0')
from gi.repository import Atk

import time

from . import braille
from . import debug
from . import messages
from . import object_properties
from . import settings
from . import settings_manager
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue

class Generator:
    """Takes accessible objects and generates a presentation for those
    objects.  See the generate method, which is the primary entry
    point."""

    def __init__(self, script, mode):
        self._mode = mode
        self._script = script
        self._activeProgressBars = {}

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

    def generateContents(self, contents, **args):
        return []

    def generateContext(self, obj, **args):
        return []

    def generate(self, obj, **args):
        return []

    def _resultElementToString(self, element, includeAll=True):
        if not includeAll:
            return str(element).replace("\n", "\\n")

        return f"\n{' ' * 18}'{element}'"

    def _debugResultInfo(self, result):
        if debug.LEVEL_ALL < debug.debugLevel:
            return

        info = f"{' ' * 18}{self._mode.upper()} GENERATOR: Results: "
        info += f"{' '.join(map(self._resultElementToString, result))}"
        debug.printMessage(debug.LEVEL_ALL, info)

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
        # Subclasses must override this.
        return []

    def _fallBackOnDescriptionForName(self, obj, **args):
        role = args.get('role', AXObject.get_role(obj))
        if role == Atspi.Role.LABEL:
            return False

        return True

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
        result = []
        self._script.point_of_reference['usedDescriptionForName'] = False
        name = AXObject.get_name(obj)
        role = args.get('role', AXObject.get_role(obj))
        parent = AXObject.get_parent(obj)
        if name:
            result.append(name)
        elif self._fallBackOnDescriptionForName(obj, **args):
            description = AXObject.get_description(obj)
            if description:
                result.append(description)
                self._script.point_of_reference['usedDescriptionForName'] = True
            else:
                link = None
                if role == Atspi.Role.LINK:
                    link = obj
                elif AXUtilities.is_link(parent):
                    link = parent
                if link:
                    basename = AXHypertext.get_link_basename(link, remove_extension=True)
                    if basename:
                        result.append(basename)
        # To make the unlabeled icons in gnome-panel more accessible.
        if not result and role == Atspi.Role.ICON and AXUtilities.is_panel(parent):
            return self._generateName(parent)

        return result

    def _generatePlaceholderText(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the 'placeholder' text. This is typically text that
        serves as a functional label and is found in a text widget until
        that widget is given focus at which point the text is removed,
        the assumption being that the user was able to see the text prior
        to giving the widget focus.
        """
        attrs = AXObject.get_attributes_dict(obj)
        placeholder = attrs.get('placeholder-text')
        if placeholder and placeholder != AXObject.get_name(obj):
            return [placeholder]

        placeholder = attrs.get('placeholder')
        if placeholder and placeholder != AXObject.get_name(obj):
            return [placeholder]

        return []

    def _generateLabelAndName(self, obj, **args):
        """Returns the label and the name as an array of strings for speech
        and braille.  The name will only be present if the name is
        different from the label.
        """

        if AXUtilities.is_menu(obj, args.get("role")) \
           and self._script.utilities.isPopupMenuForCurrentItem(obj):
            tokens = ["GENERATOR:", obj, "is popup menu for current item."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        result = []
        label = self._generateLabel(obj, **args)
        name = self._generateName(obj, **args)
        role = args.get('role', AXObject.get_role(obj))
        if not (label or name) and role == Atspi.Role.TABLE_CELL:
            descendant = self._script.utilities.realActiveDescendant(obj)
            name = self._generateName(descendant)

        # If we don't have a label, always use the name.
        if not label:
            return name

        result.extend(label)
        if not name:
            return result

        if self._script.utilities.stringsAreRedundant(name[0], label[0]):
            if len(name[0]) < len(label[0]):
                return label
            return name

        result.extend(name)
        if result:
            return result

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_autocomplete(parent):
            result = self._generateLabelAndName(parent, **args)

        return result

    def _generateLabelOrName(self, obj, **args):
        """Returns the label as an array of strings for speech and braille.
        If the label cannot be found, the name will be used instead.
        If the name cannot be found, an empty array will be returned.
        """
        result = self._generateLabel(obj, **args)
        if not result:
            result = self._generateName(obj, **args)

        return result

    def _generateUnrelatedLabelsOrDescription(self, obj, **args):
        result = self._generateDescription(obj, **args)
        if result:
            self._script.point_of_reference['usedDescriptionForUnrelatedLabels'] = True
            return result

        result = self._generateUnrelatedLabels(obj, **args)
        if result:
            self._script.point_of_reference['usedDescriptionForUnrelatedLabels'] = False

        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings fo use by speech and braille that
        represent the description of the object, if that description
        is different from that of the name and label.
        """

        if self._script.point_of_reference.get('usedDescriptionForName'):
            return []

        if self._script.point_of_reference.get('usedDescriptionForAlert'):
            return []

        if self._script.point_of_reference.get('usedDescriptionForUnrelatedLabels'):
            return []

        description = AXObject.get_description(obj) \
            or self._script.utilities.displayedDescription(obj) or ""
        if not description:
            return []

        name = AXObject.get_name(obj)
        role = args.get('role', AXObject.get_role(obj))

        try:
            tokens = self._script.formatting[self._mode][role][args.get('formatType')].split()
            isLabelAndName = 'labelAndName' in tokens
            isLabelOrName = 'labelOrName' in tokens
        except Exception:
            isLabelAndName = False
            isLabelOrName = False

        canUse = True
        label = self._script.utilities.displayedLabel(obj) or ""
        if isLabelAndName:
            canUse = not self._script.utilities.stringsAreRedundant(name, description) \
                     and not self._script.utilities.stringsAreRedundant(label, description)
        elif isLabelOrName and label:
            canUse = not self._script.utilities.stringsAreRedundant(label, description)
        else:
            canUse = not self._script.utilities.stringsAreRedundant(name, description)

        if not canUse:
            return []

        return [description]

    def _generateLabel(self, obj, **args):
        """Returns the label for an object as an array of strings for use by
        speech and braille.  The label is determined by the displayedLabel
        method of the script utility, and an empty array will be returned if
        no label can be found.
        """
        result = []
        label = self._script.utilities.displayedLabel(obj)
        if label:
            result.append(label)
        return result

    def _generateStatusBar(self, obj, **args):
        """Returns an array of strings that represent a status bar."""

        return []

    def _generateTermValueCount(self, obj, **args):
        return []

    #####################################################################
    #                                                                   #
    # Image information                                                 #
    #                                                                   #
    #####################################################################

    def _generateImageDescription(self, obj, **args ):
        """Returns an array of strings for use by speech and braille that
        represent the description of the image on the object, if it
        exists.  Otherwise, an empty array is returned.
        """

        description = AXObject.get_image_description(obj)
        if description:
            return [description]
        return []

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generateClickable(self, obj, **args):
        return []

    def _generateHasLongDesc(self, obj, **args):
        return []

    def _generateHasDetails(self, obj, **args):
        return []

    def _generateDetailsFor(self, obj, **args):
        return []

    def _generateAllDetails(self, obj, **args):
        return []

    def _generateHasPopup(self, obj, **args):
        return []

    def _generateAvailability(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the grayed/sensitivity/availability state of the
        object, but only if it is insensitive (i.e., grayed out and
        inactive).  Otherwise, and empty array will be returned.
        """

        if AXUtilities.is_sensitive(obj):
            return []

        if self._mode == "braille":
            return [object_properties.STATE_INSENSITIVE_BRAILLE]
        if self._mode == "speech":
            return [object_properties.STATE_INSENSITIVE_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_INSENSITIVE_SOUND]

        return []

    def _generateInvalid(self, obj, **args):
        error = self._script.utilities.getError(obj)
        if not error:
            return []

        if self._mode == "braille":
            indicators = object_properties.INVALID_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.INVALID_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.INVALID_INDICATORS_SOUND
        else:
            return []

        result = []
        if error == 'spelling':
            indicator = indicators[1]
        elif error == 'grammar':
            indicator = indicators[2]
        else:
            indicator = indicators[0]

        errorMessage = self._script.utilities.getErrorMessage(obj)
        if errorMessage:
            result.append(f"{indicator}: {errorMessage}")
        else:
            result.append(indicator)

        return result

    def _generateRequired(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the required state of the object, but only if it is
        required (i.e., it is in a dialog requesting input and the
        user must give it a value).  Otherwise, and empty array will
        be returned.
        """

        is_required = AXUtilities.is_required(obj)
        if not is_required and AXUtilities.is_radio_button(obj):
            is_required = AXUtilities.is_required(AXObject.get_parent(obj))
        if not is_required:
            return []

        if self._mode == "braille":
            return [object_properties.STATE_REQUIRED_BRAILLE]
        if self._mode == "speech":
            return [object_properties.STATE_REQUIRED_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_REQUIRED_SOUND]

        return []

    def _generateReadOnly(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the read only state of this object, but only if it
        is read only (i.e., it is a text area that cannot be edited).
        """

        if not (AXUtilities.is_read_only(obj) or self._script.utilities.isReadOnlyTextArea(obj)):
            return []

        if self._mode == "braille":
            return [object_properties.STATE_READ_ONLY_BRAILLE]
        if self._mode == "speech":
            return [object_properties.STATE_READ_ONLY_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_READ_ONLY_SOUND]

        return []

    def _generateCellCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes that are in a table. An empty array will be
        returned if this is not a checkable cell.
        """
        result = []
        if self._script.utilities.hasMeaningfulToggleAction(obj):
            oldRole = self._overrideRole(Atspi.Role.CHECK_BOX, args)
            result.extend(self.generate(obj, **args))
            self._restoreRole(oldRole, args)

        return result

    def _generateCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """

        if self._mode == "braille":
            indicators = object_properties.CHECK_BOX_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.CHECK_BOX_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.CHECK_BOX_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj):
            return [indicators[1]]
        if AXUtilities.is_indeterminate(obj):
            return [indicators[2]]
        return [indicators[0]]

    def _generateRadioState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """

        if self._mode == "braille":
            indicators = object_properties.RADIO_BUTTON_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.RADIO_BUTTON_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.RADIO_BUTTON_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj):
            return [indicators[1]]
        return [indicators[0]]

    def _generateChildWidget(self, obj, **args):
        widgetRoles = [Atspi.Role.CHECK_BOX,
                       Atspi.Role.COMBO_BOX,
                       Atspi.Role.PUSH_BUTTON,
                       Atspi.Role.RADIO_BUTTON,
                       Atspi.Role.SLIDER,
                       Atspi.Role.TOGGLE_BUTTON]

        def isWidget(x):
            return AXObject.get_role(x) in widgetRoles

        # For GtkListBox, such as those found in the control center
        if AXUtilities.is_list_box(AXObject.get_parent(obj)):
            widget = AXObject.find_descendant(obj, isWidget)
            if widget:
                return self.generate(widget, includeContext=False)

        return []

    def _generateSwitchState(self, obj, **args):
        if self._mode == "braille":
            indicators = object_properties.SWITCH_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.SWITCH_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.SWITCH_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj) or AXUtilities.is_pressed(obj):
            return [indicators[1]]
        return [indicators[0]]

    def _generateToggleState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """

        if self._mode == "braille":
            indicators = object_properties.TOGGLE_BUTTON_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.TOGGLE_BUTTON_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.TOGGLE_BUTTON_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj) or AXUtilities.is_pressed(obj):
            return [indicators[1]]
        return [indicators[0]]

    def _generateCheckedStateIfCheckable(self, obj, **args):
        if AXUtilities.is_checkable(obj) or AXUtilities.is_check_menu_item(obj):
            return self._generateCheckedState(obj, **args)

        if AXUtilities.is_checked(obj):
            return self._generateCheckedState(obj, **args)

        return []

    def _generateMenuItemCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the menu item.
        """
        if self._mode == "braille":
            indicators = object_properties.CHECK_BOX_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.CHECK_BOX_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.CHECK_BOX_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj):
            return [indicators[1]]
        return [indicators[0]]

    def _generateExpandableState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the expanded/collapsed state of an object, such as a
        tree node. If the object is not expandable, an empty array
        will be returned.
        """
        if self._mode == "braille":
            indicators = object_properties.EXPANSION_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.EXPANSION_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.EXPANSION_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_collapsed(obj):
            return [indicators[0]]
        if AXUtilities.is_expanded(obj):
            return [indicators[1]]
        if AXUtilities.is_expandable(obj):
            return [indicators[0]]
        return []

    def _generateMultiselectableState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the multiselectable state of
        the object.  This is typically for list boxes. If the object
        is not multiselectable, an empty array will be returned.
        """

        if not (AXUtilities.is_multiselectable(obj) and AXObject.get_child_count(obj)):
            return []

        # TODO - JD: There is no braille property and the braille generation
        # doesn't generate this state. Shouldn't it be presented in braille?

        if self._mode == "speech":
            return [object_properties.STATE_MULTISELECT_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_MULTISELECT_SOUND]
        return []

    #####################################################################
    #                                                                   #
    # Table interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateRowHeader(self, obj, **args):
        """Returns an array of strings to be used in speech and braille that
        represent the row header for an object that is in a table, if
        it exists.  Otherwise, an empty array is returned.
        """

        if args.get('readingRow'):
            return []

        result = []
        if args.get('newOnly'):
            headers = AXTable.get_new_row_headers(obj, args.get('priorObj'))
        else:
            headers = AXTable.get_row_headers(obj)

        tokens = []
        for header in headers:
            token = self._script.utilities.displayedText(header)
            if token and token.strip():
                tokens.append(token.strip())

        if not tokens:
            return result

        text = ". ".join(tokens)
        roleString =  self.getLocalizedRoleName(obj, role=Atspi.Role.ROW_HEADER)
        if args.get('mode') == 'speech':
            if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
               and args.get('formatType') not in ['basicWhereAmI', 'detailedWhereAmI']:
                text = f"{text} {roleString}"
        elif args.get('mode') == 'braille':
            text = f"{text} {roleString}"

        result.append(text)
        return result

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned.
        """
        result = []
        if args.get('newOnly'):
            headers = AXTable.get_new_column_headers(obj, args.get('priorObj'))
        else:
            headers = AXTable.get_column_headers(obj)

        tokens = []
        for header in headers:
            token = self._script.utilities.displayedText(header)
            if token and token.strip():
                tokens.append(token.strip())

        if not tokens:
            return result

        text = ". ".join(tokens)
        roleString =  self.getLocalizedRoleName(obj, role=Atspi.Role.COLUMN_HEADER)
        if args.get('mode') == 'speech':
            if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
               and args.get('formatType') not in ['basicWhereAmI', 'detailedWhereAmI']:
                text = f"{text} {roleString}"
        elif args.get('mode') == 'braille':
            text = f"{text} {roleString}"

        result.append(text)
        return result

    def _generateSortOrder(self, obj, **args):
        description = self._script.utilities.getSortOrderDescription(obj)
        if not description:
            return []

        return [description]

    def _generateColumnHeaderIfToggleAndNoText(self, obj, **args):
        """If this table cell has a "toggle" action, and doesn't have any
        label associated with it then also speak the table column
        header.  See Orca bug #455230 for more details.
        """
        # If we're reading just a single cell in speech, the new
        # header portion is going to give us this information.
        #
        if args['mode'] == 'speech' and not args.get('readingRow', False):
            return []

        result = []
        descendant = self._script.utilities.realActiveDescendant(obj)
        label = self._script.utilities.displayedText(descendant)
        if not label and self._script.utilities.hasMeaningfulToggleAction(obj):
              headers = AXTable.get_column_headers(obj)
              if (headers):
                result.append(AXObject.get_name(headers[0]))
        return result

    def _generateRealTableCell(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to
        complexity in the code.  This method is used to return an
        array of strings for use by speech and braille for a single
        table cell itself.  The string, 'blank', is added for empty
        cells.
        """
        result = []
        oldRole = self._overrideRole('REAL_ROLE_TABLE_CELL', args)
        result.extend(self.generate(obj, **args))
        self._restoreRole(oldRole, args)
        return result

    def _generateTable(self, obj, **args):
        """Returns an array of strings for use by speech and braille to present
        the size of a table."""

        if self._script.utilities.isLayoutOnly(obj):
            return []

        if self._script.utilities.isSpreadSheetTable(obj):
            return []

        rows = AXTable.get_row_count(obj)
        cols = AXTable.get_column_count(obj)

        # This suggests broken or missing table interface.
        if (rows < 0 or cols < 0) \
           and not self._script.utilities.rowOrColumnCountUnknown(obj):
            return []

        # This can happen if an author uses ARIA incorrectly, e.g. a grid whose
        # immediate child is a gridcell rather than a row. In that case, just
        # announce the role name.
        if rows == 0 and cols == 0:
            return self._generateRoleName(obj, **args)

        return [messages.tableSize(rows, cols)]

    def _generateTableCellRow(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to complexity in
        the code.  This method is used to return an array of strings
        (and possibly voice and audio specifications) for an entire row
        in a table if that's what the user has requested and if the row
        has changed.  Otherwise, it will return an array for just the
        current cell.
        """

        presentAll = args.get('readingRow') is True \
            or args.get('formatType') == 'detailedWhereAmI' \
            or self._script.utilities.shouldReadFullRow(obj, args.get('priorObj'))

        if not presentAll:
            return self._generateRealTableCell(obj, **args)

        args['readingRow'] = True
        result = []
        cells = self._script.utilities.getShowingCellsInSameRow(
            obj, forceFullRow=not self._script.utilities.isSpreadSheetCell(obj))

        row = AXObject.find_ancestor(obj, AXUtilities.is_table_row)
        if row and AXObject.get_name(row) and not self._script.utilities.isLayoutOnly(row):
            return self.generate(row)

        # Remove any pre-calcuated values which only apply to obj and not row cells.
        doNotInclude = ['startOffset', 'endOffset', 'string']
        otherCellArgs = args.copy()
        for arg in doNotInclude:
            otherCellArgs.pop(arg, None)

        for cell in cells:
            if cell == obj:
                cellResult = self._generateRealTableCell(cell, **args)
            else:
                cellResult = self._generateRealTableCell(cell, **otherCellArgs)
            if cellResult and result and self._mode == 'braille':
                result.append(braille.Region(object_properties.TABLE_CELL_DELIMITER_BRAILLE))
            result.extend(cellResult)

        result.extend(self._generatePositionInList(obj, **args))
        return result

    #####################################################################
    #                                                                   #
    # Text interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateExpandedEOCs(self, obj, **args):
        """Returns the expanded embedded object characters for an object."""
        return []

    def _generateSubstring(self, obj, **args):
        start = args.get('startOffset')
        end = args.get('endOffset')
        if start is None or end is None:
            return []

        substring = args.get('string', self._script.utilities.substring(obj, start, end))
        if substring and self._script.EMBEDDED_OBJECT_CHARACTER not in substring:
            return [substring]

        return []

    def _generateStartOffset(self, obj, **args):
        return args.get('startOffset')

    def _generateEndOffset(self, obj, **args):
        return args.get('endOffset')

    def _generateCaretOffset(self, obj, **args):
        return args.get('caretOffset')

    def _generateCurrentLineText(self, obj, **args ):
        """Returns an array of strings for use by speech and braille
        that represents the current line of text, if
        this is a text object.  [[[WDW - consider returning an empty
        array if this is not a text object.]]]
        """
        result = self._generateSubstring(obj, **args)
        if result:
            return result

        text = AXText.get_line_at_offset(obj)[0]
        if text and self._script.EMBEDDED_OBJECT_CHARACTER not in text:
            return [text]

        return []

    def _generateDisplayedText(self, obj, **args ):
        """Returns an array of strings for use by speech and braille that
        represents all the text being displayed by the object.
        """
        result = self._generateSubstring(obj, **args)
        if result:
            return result

        displayedText = self._script.utilities.displayedText(obj)
        if not displayedText:
            return []

        return [displayedText]

    #####################################################################
    #                                                                   #
    # Tree interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateNodeLevel(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the tree node level of the object, or an empty
        array if the object is not a tree node.
        """

        level = self._script.utilities.nodeLevel(obj)
        if level < 0:
            return []

        if self._mode == "braille":
            return [object_properties.NODE_LEVEL_BRAILLE % (level + 1)]
        if self._mode == "speech":
            return [object_properties.NODE_LEVEL_SPEECH % (level + 1)]
        return []

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateValue(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the value of the object.  This is typically the
        numerical value, but may also be the text of the 'value'
        attribute if it exists on the object.  [[[WDW - we should
        consider returning an empty array if there is no value.
        """

        if AXUtilities.is_combo_box(obj, args.get("role")):
            value = self._script.utilities.getComboBoxValue(obj)
            return [value]

        if AXUtilities.is_separator(obj, args.get("role")) and not AXUtilities.is_focused(obj):
            return []

        result = AXValue.get_current_value_text(obj)
        if result:
            return [result]
        return []

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _generateApplicationName(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the name of the application for the object.
        """
        result = []
        name = AXObject.get_name(AXObject.get_application(obj))
        if name:
            result.append(name)
        return result

    def _generateNestingLevel(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the nesting level of an object in a list.
        """
        start = args.get('startOffset')
        end = args.get('endOffset')
        if start is not None and end is not None:
            return []

        level = self._script.utilities.nestingLevel(obj)
        if not level:
            return []

        if self._mode == "braille":
            return [object_properties.NESTING_LEVEL_BRAILLE % (level)]
        if self._mode == "speech":
            return [object_properties.NESTING_LEVEL_SPEECH % (level)]
        return []

    def _generateRadioButtonGroup(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the radio button group label for the object, or an
        empty array if the object has no such label.
        """
        if not AXUtilities.is_radio_button(obj):
            return []

        radioGroupLabel = None
        labels = AXUtilities.get_is_labelled_by(obj, False)
        if labels:
            radioGroupLabel = labels[0]
        if radioGroupLabel:
            return [self._script.utilities.displayedText(radioGroupLabel)]

        parent = AXObject.get_parent_checked(obj)
        while parent:
            if AXUtilities.is_panel(parent) or AXUtilities.is_filler(parent):
                label = self._generateLabelAndName(parent)
                if label:
                    return label
            parent = AXObject.get_parent_checked(parent)
        return []

    def _generateRealActiveDescendantDisplayedText(self, obj, **args ):
        """Objects, such as tables and trees, can represent individual cells
        via a complicated nested hierarchy.  This method returns an
        array of strings for use by speech and braille that represents
        the text actually being painted in the cell, if it can be
        found.  Otherwise, an empty array is returned.
        """
        rad = self._script.utilities.realActiveDescendant(obj)

        if not (AXUtilities.is_table_cell(rad) and AXObject.get_child_count(rad)):
            return self._generateDisplayedText(rad, **args)

        content = set([self._script.utilities.displayedText(x).strip() \
            for x in AXObject.iter_children(rad)])
        rv = " ".join(filter(lambda x: x, content))
        if not rv:
            return self._generateDisplayedText(rad, **args)
        return [rv]

    def _generateRealActiveDescendantRoleName(self, obj, **args ):
        """Objects, such as tables and trees, can represent individual cells
        via a complicated nested hierarchy.  This method returns an
        array of strings for use by speech and braille that represents
        the role of the object actually being painted in the cell.
        """
        rad = self._script.utilities.realActiveDescendant(obj)
        args['role'] = AXObject.get_role(rad)
        return self._generateRoleName(rad, **args)

    def _generateNamedContainingPanel(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the nearest ancestor of an object which is a named panel.
        """
        result = []
        parent = AXObject.get_parent_checked(obj)
        while parent:
            if AXUtilities.is_panel(parent):
                label = self._generateLabelAndName(parent)
                if label:
                    result.extend(label)
                    break
            parent = AXObject.get_parent_checked(parent)
        return result

    def _generatePageSummary(self, obj, **args):
        return []

    def _generatePositionInList(self, obj, **args):
        return []

    def _generateProgressBarIndex(self, obj, **args):
        return []

    def _generateProgressBarValue(self, obj, **args):
        return []

    def _getProgressBarUpdateInterval(self):
        return int(settings_manager.get_manager().get_setting('progressBarUpdateInterval'))

    def _shouldPresentProgressBarUpdate(self, obj, **args):
        percent = AXValue.get_value_as_percent(obj)
        lastTime, lastValue = self.getProgressBarUpdateTimeAndValue(obj, type=self)
        if percent == lastValue:
            tokens = ["GENERATOR: Not presenting update for", obj, ". Value still", percent]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if percent == 100:
            return True

        interval = int(time.time() - lastTime)
        return interval >= self._getProgressBarUpdateInterval()

    def _cleanUpCachedProgressBars(self):
        bars = list(filter(AXObject.is_valid, self._activeProgressBars))
        self._activeProgressBars = {x:self._activeProgressBars.get(x) for x in bars}

    def _getMostRecentProgressBarUpdate(self):
        self._cleanUpCachedProgressBars()
        if not self._activeProgressBars.values():
            return None, 0.0, None

        sortedValues = sorted(self._activeProgressBars.values(), key=lambda x: x[0])
        prevTime, prevValue = sortedValues[-1]
        return list(self._activeProgressBars.keys())[-1], prevTime, prevValue

    def getProgressBarNumberAndCount(self, obj):
        self._cleanUpCachedProgressBars()
        if obj not in self._activeProgressBars:
            self._activeProgressBars[obj] = 0.0, None

        thisValue = self.getProgressBarUpdateTimeAndValue(obj)
        index = list(self._activeProgressBars.values()).index(thisValue)
        return index + 1, len(self._activeProgressBars)

    def getProgressBarUpdateTimeAndValue(self, obj, **args):
        if obj not in self._activeProgressBars:
            self._activeProgressBars[obj] = 0.0, None

        return self._activeProgressBars.get(obj)

    def setProgressBarUpdateTimeAndValue(self, obj, lastTime=None, lastValue=None):
        lastTime = lastTime or time.time()
        lastValue = lastValue or AXValue.get_value_as_percent(obj)
        self._activeProgressBars[obj] = lastTime, lastValue

    def _getAlternativeRole(self, obj, **args):
        if AXUtilities.is_math_related(obj):
            if AXUtilities.is_math_sub_or_super_script(obj):
                return 'ROLE_MATH_SCRIPT_SUBSUPER'
            if AXUtilities.is_math_under_or_over_script(obj):
                return 'ROLE_MATH_SCRIPT_UNDEROVER'
            if AXUtilities.is_math_multi_script(obj):
                return 'ROLE_MATH_MULTISCRIPT'
            if AXUtilities.is_math_enclose(obj):
                return 'ROLE_MATH_ENCLOSED'
            if AXUtilities.is_math_fenced(obj):
                return 'ROLE_MATH_FENCED'
            if AXUtilities.is_math_table(obj):
                return 'ROLE_MATH_TABLE'
            if AXUtilities.is_math_table_row(obj):
                return 'ROLE_MATH_TABLE_ROW'
        if AXUtilities.is_dpub(obj):
            if AXUtilities.is_landmark(obj):
                return 'ROLE_DPUB_LANDMARK'
            if AXUtilities.is_section(obj):
                return 'ROLE_DPUB_SECTION'
        if AXUtilities.is_switch(obj):
            return 'ROLE_SWITCH'
        if self._script.utilities.isAnchor(obj):
            return Atspi.Role.STATIC
        if AXUtilities.is_block_quote(obj):
            return Atspi.Role.BLOCK_QUOTE
        if AXUtilities.is_comment(obj):
            return Atspi.Role.COMMENT
        if self._script.utilities.isContentError(obj):
            return 'ROLE_CONTENT_ERROR'
        if AXUtilities.is_description_list(obj):
            return Atspi.Role.DESCRIPTION_LIST
        if AXUtilities.is_description_term(obj):
            return Atspi.Role.DESCRIPTION_TERM
        if AXUtilities.is_description_value(obj):
            return Atspi.Role.DESCRIPTION_VALUE
        if AXUtilities.is_feed_article(obj):
            return 'ROLE_ARTICLE_IN_FEED'
        if AXUtilities.is_feed(obj):
            return 'ROLE_FEED'
        if AXUtilities.is_landmark(obj):
            if AXUtilities.is_landmark_region(obj):
                return 'ROLE_REGION'
            return Atspi.Role.LANDMARK
        if self._script.utilities.isFocusableLabel(obj):
            return Atspi.Role.LIST_ITEM
        if self._script.utilities.isDocument(obj) and AXObject.supports_image(obj):
            return Atspi.Role.IMAGE

        return args.get('role', AXObject.get_role(obj))

    def getLocalizedRoleName(self, obj, **args):
        role = args.get('role', AXObject.get_role(obj))

        if AXObject.supports_value(obj):
            if AXUtilities.is_horizontal_slider(obj):
                return object_properties.ROLE_SLIDER_HORIZONTAL
            if AXUtilities.is_vertical_slider(obj):
                return object_properties.ROLE_SLIDER_VERTICAL
            if AXUtilities.is_horizontal_scrollbar(obj):
                return object_properties.ROLE_SCROLL_BAR_HORIZONTAL
            if AXUtilities.is_vertical_scrollbar(obj):
                return object_properties.ROLE_SCROLL_BAR_VERTICAL
            if AXUtilities.is_horizontal_separator(obj):
                return object_properties.ROLE_SPLITTER_HORIZONTAL
            if AXUtilities.is_vertical_separator(obj):
                return object_properties.ROLE_SPLITTER_VERTICAL
            if AXUtilities.is_split_pane(obj) \
               and (AXUtilities.is_focused(obj) or args.get('alreadyFocused', False)):
                # The splitter has the opposite orientation of the split pane.
                if AXUtilities.is_horizontal(obj):
                    return object_properties.ROLE_SPLITTER_VERTICAL
                if AXUtilities.is_vertical(obj):
                    return object_properties.ROLE_SPLITTER_HORIZONTAL

        if AXUtilities.is_suggestion(obj):
            return object_properties.ROLE_CONTENT_SUGGESTION

        if AXUtilities.is_feed(obj):
            return object_properties.ROLE_FEED

        if AXUtilities.is_figure(obj):
            return object_properties.ROLE_FIGURE

        if self._script.utilities.isMenuButton(obj):
            return object_properties.ROLE_MENU_BUTTON

        if AXUtilities.is_switch(obj):
            return object_properties.ROLE_SWITCH

        if AXUtilities.is_dpub(obj):
            if AXUtilities.is_landmark(obj):
                if AXUtilities.is_dpub_acknowledgments(obj):
                    return object_properties.ROLE_ACKNOWLEDGMENTS
                if AXUtilities.is_dpub_afterword(obj):
                    return object_properties.ROLE_AFTERWORD
                if AXUtilities.is_dpub_appendix(obj):
                    return object_properties.ROLE_APPENDIX
                if AXUtilities.is_dpub_bibliography(obj):
                    return object_properties.ROLE_BIBLIOGRAPHY
                if AXUtilities.is_dpub_chapter(obj):
                    return object_properties.ROLE_CHAPTER
                if AXUtilities.is_dpub_conclusion(obj):
                    return object_properties.ROLE_CONCLUSION
                if AXUtilities.is_dpub_credits(obj):
                    return object_properties.ROLE_CREDITS
                if AXUtilities.is_dpub_endnotes(obj):
                    return object_properties.ROLE_ENDNOTES
                if AXUtilities.is_dpub_epilogue(obj):
                    return object_properties.ROLE_EPILOGUE
                if AXUtilities.is_dpub_errata(obj):
                    return object_properties.ROLE_ERRATA
                if AXUtilities.is_dpub_foreword(obj):
                    return object_properties.ROLE_FOREWORD
                if AXUtilities.is_dpub_glossary(obj):
                    return object_properties.ROLE_GLOSSARY
                if AXUtilities.is_dpub_index(obj):
                    return object_properties.ROLE_INDEX
                if AXUtilities.is_dpub_introduction(obj):
                    return object_properties.ROLE_INTRODUCTION
                if AXUtilities.is_dpub_pagelist(obj):
                    return object_properties.ROLE_PAGELIST
                if AXUtilities.is_dpub_part(obj):
                    return object_properties.ROLE_PART
                if AXUtilities.is_dpub_preface(obj):
                    return object_properties.ROLE_PREFACE
                if AXUtilities.is_dpub_prologue(obj):
                    return object_properties.ROLE_PROLOGUE
                if AXUtilities.is_dpub_toc(obj):
                    return object_properties.ROLE_TOC
            elif role == "ROLE_DPUB_SECTION":
                if AXUtilities.is_dpub_abstract(obj):
                    return object_properties.ROLE_ABSTRACT
                if AXUtilities.is_dpub_colophon(obj):
                    return object_properties.ROLE_COLOPHON
                if AXUtilities.is_dpub_credit(obj):
                    return object_properties.ROLE_CREDIT
                if AXUtilities.is_dpub_dedication(obj):
                    return object_properties.ROLE_DEDICATION
                if AXUtilities.is_dpub_epigraph(obj):
                    return object_properties.ROLE_EPIGRAPH
                if AXUtilities.is_dpub_example(obj):
                    return object_properties.ROLE_EXAMPLE
                if AXUtilities.is_dpub_pullquote(obj):
                    return object_properties.ROLE_PULLQUOTE
                if AXUtilities.is_dpub_qna(obj):
                    return object_properties.ROLE_QNA
            elif role == Atspi.Role.LIST_ITEM:
                if AXUtilities.is_dpub_biblioentry(obj):
                    return object_properties.ROLE_BIBLIOENTRY
                if AXUtilities.is_dpub_endnote(obj):
                    return object_properties.ROLE_ENDNOTE
            else:
                if AXUtilities.is_dpub_cover(obj):
                    return object_properties.ROLE_COVER
                if AXUtilities.is_dpub_pagebreak(obj):
                    return object_properties.ROLE_PAGEBREAK
                if AXUtilities.is_dpub_subtitle(obj):
                    return object_properties.ROLE_SUBTITLE

        if AXUtilities.is_landmark(obj):
            if AXUtilities.is_landmark_without_type(obj):
                return ''
            if AXUtilities.is_landmark_banner(obj):
                return object_properties.ROLE_LANDMARK_BANNER
            if AXUtilities.is_landmark_complementary(obj):
                return object_properties.ROLE_LANDMARK_COMPLEMENTARY
            if AXUtilities.is_landmark_contentinfo(obj):
                return object_properties.ROLE_LANDMARK_CONTENTINFO
            if AXUtilities.is_landmark_main(obj):
                return object_properties.ROLE_LANDMARK_MAIN
            if AXUtilities.is_landmark_navigation(obj):
                return object_properties.ROLE_LANDMARK_NAVIGATION
            if AXUtilities.is_landmark_region(obj):
                return object_properties.ROLE_LANDMARK_REGION
            if AXUtilities.is_landmark_search(obj):
                return object_properties.ROLE_LANDMARK_SEARCH
            if AXUtilities.is_landmark_form(obj):
                role = Atspi.Role.FORM
        elif AXUtilities.is_comment(obj):
            role = Atspi.Role.COMMENT

        if not isinstance(role, Atspi.Role):
            try:
                return obj.getLocalizedRoleName()
            except Exception:
                return ''

        nonlocalized = Atspi.role_get_name(role)
        atkRole = Atk.role_for_name(nonlocalized)
        if atkRole == Atk.Role.INVALID:
            if role == Atspi.Role.STATUS_BAR:
                atkRole = Atk.Role.STATUSBAR
            elif role == Atspi.Role.EDITBAR:
                atkRole = Atk.Role.EDIT_BAR

        return Atk.role_get_localized_name(atkRole)

    def getStateIndicator(self, obj, **args):
        if AXUtilities.is_switch(obj):
            return self._generateSwitchState(obj, **args)

        role = args.get('role', AXObject.get_role(obj))

        if role == Atspi.Role.MENU_ITEM:
            return self._generateMenuItemCheckedState(obj, **args)

        if role in [Atspi.Role.RADIO_BUTTON, Atspi.Role.RADIO_MENU_ITEM]:
            return self._generateRadioState(obj, **args)

        if role in [Atspi.Role.CHECK_BOX, Atspi.Role.CHECK_MENU_ITEM]:
            return self._generateCheckedState(obj, **args)

        if role == Atspi.Role.TOGGLE_BUTTON:
            return self._generateToggleState(obj, **args)

        if role == Atspi.Role.TABLE_CELL:
            return self._generateCellCheckedState(obj, **args)

        return []

    def getValue(self, obj, **args):
        role = args.get('role', AXObject.get_role(obj))

        if role == Atspi.Role.PROGRESS_BAR:
            return self._generateProgressBarValue(obj, **args)

        if role in [Atspi.Role.SCROLL_BAR, Atspi.Role.SLIDER]:
            return self._generatePercentage(obj, **args)

        return []
