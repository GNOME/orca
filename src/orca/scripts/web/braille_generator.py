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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-locals

"""Produces braille presentation for accessible objects."""

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
    """Produces braille presentation for accessible objects."""

    def get_localized_role_name(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super().get_localized_role_name(obj, **args)

        role_description = self._script.utilities.getRoleDescription(obj, True)
        if role_description:
            return role_description

        return super().get_localized_role_name(obj, **args)

    def _generate_accessible_role(self, obj, **args):
        """Prevents some roles from being displayed."""

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_role(obj, **args)

        role_description = self._script.utilities.getRoleDescription(obj, True)
        if role_description:
            return [role_description]

        # TODO - JD: Can this logic be moved to the default braille generator?
        do_not_display = [Atspi.Role.FORM,
                          Atspi.Role.PARAGRAPH,
                          Atspi.Role.STATIC,
                          Atspi.Role.SECTION,
                          Atspi.Role.REDUNDANT_OBJECT,
                          Atspi.Role.UNKNOWN]

        if not AXUtilities.is_focusable(obj):
            do_not_display.extend([Atspi.Role.LIST,
                                   Atspi.Role.LIST_ITEM,
                                   Atspi.Role.COLUMN_HEADER,
                                   Atspi.Role.ROW_HEADER,
                                   Atspi.Role.TABLE_CELL,
                                   Atspi.Role.PANEL])

        if args.get("startOffset") is not None and args.get("endOffset") is not None:
            do_not_display.append(Atspi.Role.ALERT)

        result = []
        role = args.get('role', AXObject.get_role(obj))

        if AXUtilities.is_heading(obj, args.get("role")):
            level = self._script.utilities.headingLevel(obj)
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)
            return result

        if self._script.utilities.isLink(obj) \
           and obj == focus_manager.get_manager().get_locus_of_focus():
            if AXUtilities.is_image(AXObject.get_parent(obj)):
                result.append(messages.IMAGE_MAP_LINK)

        elif role not in do_not_display:
            label = AXTable.get_label_for_cell_coordinates(obj)
            if label:
                result.append(label)
            else:
                result = super()._generate_accessible_role(obj, **args)

        if args.get("index", 0) == args.get("total", 1) - 1 \
           and (AXUtilities.is_image(obj, args.get("role")) \
               or self._script.utilities.treatAsTextObject(obj)):
            heading = AXObject.find_ancestor(obj, AXUtilities.is_heading)
            if heading is not None:
                result.extend(self._generate_accessible_role(heading))

        return result

    def _generate_accessible_label(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_label(obj, **args)

        label, _objects = self._script.utilities.inferLabelFor(obj)
        if label:
            return [label]

        return super()._generate_accessible_label(obj, **args)

    def _generate_accessible_label_and_name(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_label_and_name(obj, **args)

        if self._script.utilities.isTextBlockElement(obj):
            return []

        if AXUtilities.is_editable(obj) \
           and self._script.utilities.isCodeDescendant(obj):
            return []

        role = args.get('role', AXObject.get_role(obj))
        if role == Atspi.Role.LABEL and AXObject.supports_text(obj):
            return []

        return super()._generate_accessible_label_and_name(obj, **args)

    def _generate_accessible_description(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_description(obj, **args)

        if self._script.utilities.preferDescriptionOverName(obj):
            return []

        return super()._generate_accessible_description(obj, **args)

    def _generate_accessible_name(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_name(obj, **args)

        braille_label = AXObject.get_attributes_dict(obj).get("braillelabel")
        if braille_label:
            return [braille_label]

        if self._script.utilities.preferDescriptionOverName(obj):
            return [AXObject.get_description(obj)]

        if AXObject.get_name(obj) and not self._script.utilities.hasValidName(obj):
            return []

        result = super()._generate_accessible_name(obj, **args)
        if result and result[0] and not self._script.utilities.hasExplicitName(obj):
            result[0] = result[0].strip()
        elif not result and AXUtilities.is_check_box(obj):
            grid_cell = AXObject.find_ancestor(obj, AXUtilities.is_grid_cell)
            if grid_cell:
                return super()._generate_accessible_name(grid_cell, **args)

        return result

    def _generate_real_active_descendant_displayed_text(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_real_active_descendant_displayed_text(obj, **args)

        rad = self._script.utilities.realActiveDescendant(obj)
        return self._generate_text_content(rad, **args)

    def generate_braille(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            tokens = ["WEB:", obj, "is not in document content. Calling default braille generator."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return super().generate_braille(obj, **args)

        tokens = ["WEB: Generating braille for document object", obj, args]
        debug.printTokens(debug.LEVEL_INFO, tokens, True, True)

        result = []

        args['includeContext'] = not self._script.utilities.inDocumentContent(obj)
        if self._script.utilities.isClickableElement(obj) or self._script.utilities.isLink(obj):
            args["role"] = Atspi.Role.LINK
        elif self._script.utilities.isCustomImage(obj):
            args["role"] = Atspi.Role.IMAGE
        elif self._script.utilities.isAnchor(obj):
            args["role"] = Atspi.Role.STATIC
        elif self._script.utilities.treatAsDiv(obj, offset=args.get('startOffset')):
            args["role"] = Atspi.Role.SECTION
        elif self._script.utilities.treatAsEntry(obj):
            args["role"] = Atspi.Role.ENTRY

        if AXUtilities.is_menu_item(obj):
            combo_box = AXObject.find_ancestor(obj, AXUtilities.is_combo_box)
            if combo_box and not AXUtilities.is_expanded(combo_box):
                obj = combo_box
        result.extend(super().generate_braille(obj, **args))
        del args['includeContext']
        return result

    def generate_contents(self, contents, **args):
        if not contents:
            return []

        result = []
        contents = self._script.utilities.filterContentsForPresentation(contents, True)

        document = args.get("documentFrame")
        obj, offset = self._script.utilities.getCaretContext(documentFrame=document)
        index = self._script.utilities.findObjectInContents(obj, offset, contents)

        last_region = None
        focused_region = None
        for i, content in enumerate(contents):
            acc, start, end, string = content
            regions, f_region = self.generate_braille(
                acc, startOffset=start, endOffset=end, caretOffset=offset, string=string,
                index=i, total=len(contents))
            if not regions:
                continue

            if i == index:
                focused_region = f_region

            if last_region and regions:
                last_char = next_char = ""
                if last_region.string:
                    last_char = last_region.string[-1]
                if regions[0].string:
                    next_char = regions[0].string[0]
                if self._script.utilities.needsSeparator(last_char, next_char):
                    regions.insert(0, braille.Region(" "))

            last_region = regions[-1]
            result.append(regions)

        return result, focused_region
