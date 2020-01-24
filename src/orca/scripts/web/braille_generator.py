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

import pyatspi

from orca import braille
from orca import braille_generator
from orca import debug
from orca import messages
from orca import object_properties
from orca import orca_state


class BrailleGenerator(braille_generator.BrailleGenerator):

    def __init__(self, script):
        super().__init__(script)

    def getLocalizedRoleName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super().getLocalizedRoleName(obj, **args)

        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            return roledescription

        return super().getLocalizedRoleName(obj, **args)

    def _generateRoleName(self, obj, **args):
        """Prevents some roles from being displayed."""

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateRoleName(obj, **args)

        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            return [roledescription]

        doNotDisplay = [pyatspi.ROLE_FORM,
                        pyatspi.ROLE_PARAGRAPH,
                        pyatspi.ROLE_STATIC,
                        pyatspi.ROLE_SECTION,
                        pyatspi.ROLE_REDUNDANT_OBJECT,
                        pyatspi.ROLE_UNKNOWN]

        state = obj.getState()
        if not state.contains(pyatspi.STATE_FOCUSABLE):
            doNotDisplay.extend([pyatspi.ROLE_LIST,
                                 pyatspi.ROLE_LIST_ITEM,
                                 pyatspi.ROLE_COLUMN_HEADER,
                                 pyatspi.ROLE_ROW_HEADER,
                                 pyatspi.ROLE_TABLE_CELL,
                                 pyatspi.ROLE_PANEL])

        if args.get('startOffset') is not None and args.get('endOffset') is not None:
            doNotDisplay.append(pyatspi.ROLE_ALERT)

        result = []
        role = args.get('role', obj.getRole())

        if role == pyatspi.ROLE_HEADING:
            level = self._script.utilities.headingLevel(obj)
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)

        elif self._script.utilities.isLink(obj) and obj == orca_state.locusOfFocus:
            if obj.parent.getRole() == pyatspi.ROLE_IMAGE:
                result.append(messages.IMAGE_MAP_LINK)

        elif role not in doNotDisplay:
            label = self._script.utilities.labelForCellCoordinates(obj)
            if label:
                result.append(label)
            else:
                result = super()._generateRoleName(obj, **args)

        index = args.get('index', 0)
        total = args.get('total', 1)
        if index == total - 1 and role != pyatspi.ROLE_HEADING \
           and (role == pyatspi.ROLE_IMAGE or self._script.utilities.queryNonEmptyText(obj)):
            isHeading = lambda x: x and x.getRole() == pyatspi.ROLE_HEADING
            heading = pyatspi.findAncestor(obj, isHeading)
            if heading:
                result.extend(self._generateRoleName(heading))

        return result

    def _generateLabelOrName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateLabelOrName(obj, **args)

        if self._script.utilities.isTextBlockElement(obj):
            return []

        if obj.name:
            name = obj.name
            if not self._script.utilities.hasExplicitName(obj):
                name = name.strip()
            return [name]

        return super()._generateLabelOrName(obj, **args)

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

        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_LABEL and 'Text' in pyatspi.listInterfaces(obj):
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

        if self._script.utilities.preferDescriptionOverName(obj):
            return [obj.description]

        if obj.name and not self._script.utilities.hasValidName(obj):
            return []

        result = super()._generateName(obj, **args)
        if result and result[0] and not self._script.utilities.hasExplicitName(obj):
            result[0] = result[0].strip()

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

        return self._generateDisplayedText(obj, **args)

    def _generateTableCellRow(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateTableCellRow(obj, **args)

        if not self._script.inFocusMode():
            return super()._generateTableCellRow(obj, **args)

        if not self._script.utilities.shouldReadFullRow(obj):
            return self._generateRealTableCell(obj, **args)

        isRow = lambda x: x and x.getRole() == pyatspi.ROLE_TABLE_ROW
        row = pyatspi.findAncestor(obj, isRow)
        if row and row.name and not self._script.utilities.isLayoutOnly(row):
            return self.generate(row, includeContext=False)

        return super()._generateTableCellRow(obj, **args)

    def generateBraille(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            msg = "WEB: %s is not in document content. Calling default braille generator." % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return super().generateBraille(obj, **args)

        msg = "WEB: Generating braille for document object %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)

        result = []

        args['includeContext'] = not self._script.utilities.inDocumentContent(obj)
        oldRole = None
        if self._script.utilities.isClickableElement(obj) \
           or self._script.utilities.isLink(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_LINK, args)
        elif self._script.utilities.isAnchor(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_STATIC, args)
        elif self._script.utilities.treatAsDiv(obj, offset=args.get('startOffset')):
            oldRole = self._overrideRole(pyatspi.ROLE_SECTION, args)
        elif self._script.utilities.treatAsEntry(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_ENTRY, args)

        if obj.getRole() == pyatspi.ROLE_MENU_ITEM:
            comboBox = self._script.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_COMBO_BOX], [pyatspi.ROLE_FRAME])
            if comboBox and not comboBox.getState().contains(pyatspi.STATE_EXPANDED):
                obj = comboBox
        result.extend(super().generateBraille(obj, **args))
        del args['includeContext']
        if oldRole:
            self._restoreRole(oldRole, args)

        return result

    def _generateEol(self, obj, **args):
        if self._script.utilities.isContentEditableWithEmbeddedObjects(obj):
            return []

        if obj.getState().contains(pyatspi.STATE_EDITABLE) \
           or not self._script.utilities.inDocumentContent(obj):
            return super()._generateEol(obj, **args)

        return []

    def generateContents(self, contents, **args):
        if not len(contents):
            return []

        result = []
        contents = self._script.utilities.filterContentsForPresentation(contents, True)

        obj, offset = self._script.utilities.getCaretContext(documentFrame=None)
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
