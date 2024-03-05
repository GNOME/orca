# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010-2011 Orca Team
# Copyright 2011-2015 Igalia, S.L.
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2011 Orca Team" \
                "Copyright (c) 2011-2015 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import braille
from orca import braille_generator
from orca import debug
from orca import focus_manager
from orca import messages
from orca import object_properties
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities


class BrailleGenerator(braille_generator.BrailleGenerator):

    def getLocalizedRoleName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super().getLocalizedRoleName(obj, **args)

        roledescription = self._script.utilities.getRoleDescription(obj, True)
        if roledescription:
            return roledescription

        return super().getLocalizedRoleName(obj, **args)

    def _generateRoleName(self, obj, **args):
        """Prevents some roles from being displayed."""

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateRoleName(obj, **args)

        roledescription = self._script.utilities.getRoleDescription(obj, True)
        if roledescription:
            return [roledescription]

        doNotDisplay = [Atspi.Role.FORM,
                        Atspi.Role.PARAGRAPH,
                        Atspi.Role.STATIC,
                        Atspi.Role.SECTION,
                        Atspi.Role.REDUNDANT_OBJECT,
                        Atspi.Role.UNKNOWN]

        if not AXUtilities.is_focusable(obj):
            doNotDisplay.extend([Atspi.Role.LIST,
                                 Atspi.Role.LIST_ITEM,
                                 Atspi.Role.COLUMN_HEADER,
                                 Atspi.Role.ROW_HEADER,
                                 Atspi.Role.TABLE_CELL,
                                 Atspi.Role.PANEL])

        if args.get('startOffset') is not None and args.get('endOffset') is not None:
            doNotDisplay.append(Atspi.Role.ALERT)

        result = []
        role = args.get('role', AXObject.get_role(obj))

        if role == Atspi.Role.HEADING:
            level = self._script.utilities.headingLevel(obj)
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)

        elif self._script.utilities.isLink(obj) \
                and obj == focus_manager.getManager().get_locus_of_focus():
            if AXUtilities.is_image(AXObject.get_parent(obj)):
                result.append(messages.IMAGE_MAP_LINK)

        elif role not in doNotDisplay:
            label = AXTable.get_label_for_cell_coordinates(obj)
            if label:
                result.append(label)
            else:
                result = super()._generateRoleName(obj, **args)

        index = args.get('index', 0)
        total = args.get('total', 1)
        if index == total - 1 and role != Atspi.Role.HEADING \
           and (role == Atspi.Role.IMAGE or self._script.utilities.treatAsTextObject(obj)):
            heading = AXObject.find_ancestor(obj, AXUtilities.is_heading)
            if heading is not None:
                result.extend(self._generateRoleName(heading))

        return result

    def _generateLabelOrName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateLabelOrName(obj, **args)

        if self._script.utilities.isTextBlockElement(obj):
            return []

        if AXUtilities.is_editable(obj) \
           and self._script.utilities.isCodeDescendant(obj):
            return []

        return self._generateName(obj, **args)

    def _generateLabel(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateLabel(obj, **args)

        label, objects = self._script.utilities.inferLabelFor(obj)
        if label:
            return [label]

        return super()._generateLabel(obj, **args)

    def _generateLabelAndName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateLabelAndName(obj, **args)

        if self._script.utilities.isTextBlockElement(obj):
            return []

        role = args.get('role', AXObject.get_role(obj))
        if role == Atspi.Role.LABEL and AXObject.supports_text(obj):
            return []

        return super()._generateLabelAndName(obj, **args)

    def _generateDescription(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateDescription(obj, **args)

        if self._script.utilities.preferDescriptionOverName(obj):
            return []

        return super()._generateDescription(obj, **args)

    def _generateName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateName(obj, **args)

        brailleLabel = AXObject.get_attributes_dict(obj).get("braillelabel")
        if brailleLabel:
            return [brailleLabel]

        if self._script.utilities.preferDescriptionOverName(obj):
            return [AXObject.get_description(obj)]

        if AXObject.get_name(obj) and not self._script.utilities.hasValidName(obj):
            return []

        result = super()._generateName(obj, **args)
        if result and result[0] and not self._script.utilities.hasExplicitName(obj):
            result[0] = result[0].strip()
        elif not result and AXUtilities.is_check_box(obj):
            gridCell = AXObject.find_ancestor(obj, self._script.utilities.isGridCell)
            if gridCell:
                return super()._generateName(gridCell, **args)

        return result

    def _generateExpandedEOCs(self, obj, **args):
        """Returns the expanded embedded object characters for an object."""

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateExpandedEOCs(obj, **args)

        result = []
        startOffset = args.get('startOffset', 0)
        endOffset = args.get('endOffset', -1)
        text = self._script.utilities.expandEOCs(obj, startOffset, endOffset)
        if text:
            result.append(text)

        return result

    def _generateRealActiveDescendantDisplayedText(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateRealActiveDescendantDisplayedText(obj, **args)

        rad = self._script.utilities.realActiveDescendant(obj)
        return self._generateDisplayedText(rad, **args)

    def _generateTableCellRow(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateTableCellRow(obj, **args)

        if not self._script.utilities.shouldReadFullRow(obj, args.get('priorObj')):
            return self._generateRealTableCell(obj, **args)

        row = AXObject.find_ancestor(obj, AXUtilities.is_table_row)
        if row and AXObject.get_name(row) and not self._script.utilities.isLayoutOnly(row):
            return self.generate(row, includeContext=False)

        return super()._generateTableCellRow(obj, **args)

    def generateBraille(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            tokens = ["WEB:", obj, "is not in document content. Calling default braille generator."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return super().generateBraille(obj, **args)

        tokens = ["WEB: Generating braille for document object", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = []

        args['includeContext'] = not self._script.utilities.inDocumentContent(obj)
        oldRole = None
        if self._script.utilities.isClickableElement(obj) \
           or self._script.utilities.isLink(obj):
            oldRole = self._overrideRole(Atspi.Role.LINK, args)
        elif self._script.utilities.isCustomImage(obj):
            oldRole = self._overrideRole(Atspi.Role.IMAGE, args)
        elif self._script.utilities.isAnchor(obj):
            oldRole = self._overrideRole(Atspi.Role.STATIC, args)
        elif self._script.utilities.treatAsDiv(obj, offset=args.get('startOffset')):
            oldRole = self._overrideRole(Atspi.Role.SECTION, args)
        elif self._script.utilities.treatAsEntry(obj):
            oldRole = self._overrideRole(Atspi.Role.ENTRY, args)

        if AXUtilities.is_menu_item(obj):
            comboBox = AXObject.find_ancestor(obj, AXUtilities.is_combo_box)
            if comboBox and not AXUtilities.is_expanded(comboBox):
                obj = comboBox
        result.extend(super().generateBraille(obj, **args))
        del args['includeContext']
        if oldRole:
            self._restoreRole(oldRole, args)

        return result

    def generateContents(self, contents, **args):
        if not len(contents):
            return []

        result = []
        contents = self._script.utilities.filterContentsForPresentation(contents, True)

        document = args.get("documentFrame")
        obj, offset = self._script.utilities.getCaretContext(documentFrame=document)
        index = self._script.utilities.findObjectInContents(obj, offset, contents)

        lastRegion = None
        focusedRegion = None
        for i, content in enumerate(contents):
            acc, start, end, string = content
            regions, fRegion = self.generateBraille(
                acc, startOffset=start, endOffset=end, string=string,
                index=i, total=len(contents))
            if not regions:
                continue

            if i == index:
                focusedRegion = fRegion

            if lastRegion and regions:
                if lastRegion.string:
                    lastChar = lastRegion.string[-1]
                else:
                    lastChar = ""
                if regions[0].string:
                    nextChar = regions[0].string[0]
                else:
                    nextChar = ""
                if self._script.utilities.needsSeparator(lastChar, nextChar):
                    regions.insert(0, braille.Region(" "))

            lastRegion = regions[-1]
            result.append(regions)

        return result, focusedRegion
