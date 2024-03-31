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

"""Custom script for StarOffice and OpenOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from orca import messages
from orca import settings_manager
from orca import speech_generator
from orca.ax_component import AXComponent
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities


class SpeechGenerator(speech_generator.SpeechGenerator):
    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateLabel(self, obj, **args):
        """Returns the label for an object as an array of strings (and
        possibly voice and audio specifications).  The label is
        determined by the displayedLabel method of the script utility,
        and an empty array will be returned if no label can be found.
        """
        result = []
        label = self._script.utilities.displayedLabel(obj) or ""
        if not label:
            label = self._script.utilities.displayedLabel(AXObject.get_parent(obj)) or ""
        if label:
            result.append(label.strip())
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
        return result

    def _generateName(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the name of the object.  If the object is directly
        displaying any text, that text will be treated as the name.
        Otherwise, the accessible name of the object will be used.  If
        there is no accessible name, then the description of the
        object will be used.  This method will return an empty array
        if nothing can be found.
        """

        # TODO - JD: This should be the behavior by default. But the default
        # generators call displayedText(). Once that is corrected, this method
        # can be removed.
        if AXObject.get_name(obj):
            result = [AXObject.get_name(obj)]
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
            return result

        return super()._generateName(obj, **args)

    def _generateLabelAndName(self, obj, **args):
        if not AXUtilities.is_combo_box(obj):
            return super()._generateLabelAndName(obj, **args)

        # TODO - JD: This should be the behavior by default because many
        # toolkits use the label for the name.
        result = []
        label = self._script.utilities.displayedLabel(obj) or AXObject.get_name(obj)
        if label:
            result.append(label)
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))

        name = AXObject.get_name(obj)
        if label == name or not name:
            selected = self._script.utilities.selectedChildren(obj)
            if selected:
                name = AXObject.get_name(selected[0])

        if name:
            result.append(name)
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))

        return result

    def _generateAnyTextSelection(self, obj, **args):
        comboBoxEntry = self._script.utilities.getEntryForEditableComboBox(obj)
        if comboBoxEntry:
            return super()._generateAnyTextSelection(comboBoxEntry)

        return super()._generateAnyTextSelection(obj, **args)

    def _generateAvailability(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the grayed/sensitivity/availability state of the
        object, but only if it is insensitive (i.e., grayed out and
        inactive).  Otherwise, and empty array will be returned.
        """

        result = []
        if not self._script.utilities.isSpreadSheetCell(obj):
            result.extend(speech_generator.SpeechGenerator.\
                _generateAvailability(self, obj, **args))

        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the description of the object,
        if that description is different from that of the name and
        label.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if not settings_manager.get_manager().get_setting('speakDescription'):
            return []

        if not args.get('formatType', '').endswith('WhereAmI'):
            return []

        result = []
        description = AXObject.get_description(obj)
        if description:
            # The description of some OOo paragraphs consists of the name
            # and the displayed text, with punctuation added. Try to spot
            # this and, if found, ignore the description.
            #
            text = self._script.utilities.displayedText(obj) or ""
            desc = description.replace(text, "")
            for item in AXObject.get_name(obj).split():
                desc = desc.replace(item, "")
            for char in desc.strip():
                if char.isalnum():
                    result.append(description)
                    break

        if result:
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def _generateCurrentLineText(self, obj, **args):
        if AXUtilities.is_combo_box(obj):
            entry = self._script.utilities.getEntryForEditableComboBox(obj)
            if entry:
                return super()._generateCurrentLineText(entry)
            return []

        # TODO - JD: The SayLine, etc. code should be generated and not put
        # together in the scripts. In addition, the voice crap needs to go
        # here. Then it needs to be removed from the scripts.
        text = AXText.get_line_at_offset(obj)[0]
        if not text:
            result = [messages.BLANK]
            result.extend(self.voice(string=text, obj=obj, **args))
            return result

        return super()._generateCurrentLineText(obj, **args)

    def _generateToggleState(self, obj, **args):
        """Treat toggle buttons in the toolbar specially. This is so we can
        have more natural sounding speech such as "bold on", "bold off", etc."""

        if not AXUtilities.is_toggle_button(obj, args.get("role")):
            return []

        if not AXUtilities.is_tool_bar(AXObject.get_parent(obj)):
            return super()._generateToggleState(obj, **args)

        if AXUtilities.is_checked(obj):
            result = [messages.ON]
        else:
            result = [messages.OFF]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def _generateTooLong(self, obj, **args):
        """If there is text in this spread sheet cell, compare the size of
        the text within the table cell with the size of the actual table
        cell and report back to the user if it is larger.

        Returns an indication of how many characters are greater than the size
        of the spread sheet cell, or None if the message fits.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        # TODO - JD: Can this be moved to AXText?
        result = []
        length = AXText.get_character_count(obj)
        tooLongCount = 0
        extents = AXComponent.get_rect(obj)
        for i in range(length):
            rect = AXText.get_character_rect(obj, i)
            if rect.x < extents.x:
                tooLongCount += 1
            elif rect.x + rect.width > extents.x + extents.width:
                tooLongCount += length - i
                break
        if tooLongCount > 0:
            result = [messages.charactersTooLong(tooLongCount)]
        if result:
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def _generateHasFormula(self, obj, **args):
        formula = AXTable.get_cell_formula(obj)
        if not formula:
            return []

        if args.get("formatType") == "basicWhereAmI":
            result = [f"{messages.HAS_FORMULA}. {formula}"]
        else:
            result = [messages.HAS_FORMULA]

        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def _generateRealTableCell(self, obj, **args):
        """Get the speech for a table cell. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell

        Returns a list of utterances to be spoken for the object.
        """

        if self._script.inSayAll():
            return []

        result = super()._generateRealTableCell(obj, **args)

        if not self._script.utilities.isSpreadSheetCell(obj):
            if self._script.get_table_navigator().last_input_event_was_navigation_command():
                return result

            if settings_manager.get_manager().get_setting('speakCellCoordinates'):
                result.append(AXObject.get_name(obj))
            return result

        isBasicWhereAmI = args.get('formatType') == 'basicWhereAmI'
        speakCoordinates = settings_manager.get_manager().get_setting('speakSpreadsheetCoordinates')
        if speakCoordinates or isBasicWhereAmI:
            label = AXTable.get_label_for_cell_coordinates(obj) \
                or self._script.utilities.spreadSheetCellName(obj)
            result.append(label)

        if self._script.utilities.shouldReadFullRow(obj, args.get('priorObj')):
            if self._script.utilities.cellRowChanged(obj):
                return result

        tooLong = self._generateTooLong(obj, **args)
        if tooLong:
            result.extend(self._generatePause(obj, **args))
            result.extend(tooLong)

        hasFormula = self._generateHasFormula(obj, **args)
        if hasFormula:
            result.extend(self._generatePause(obj, **args))
            result.extend(hasFormula)

        if result == speech_generator.PAUSE:
            result = [messages.BLANK]
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))

        return result

    def _generateTableCellRow(self, obj, **args):
        if not self._script.utilities.shouldReadFullRow(obj, args.get('priorObj')):
            return self._generateRealTableCell(obj, **args)

        if not self._script.utilities.isSpreadSheetCell(obj):
            return super()._generateTableCellRow(obj, **args)

        cells = self._script.utilities.getShowingCellsInSameRow(obj)
        if not cells:
            return []

        result = []
        for cell in cells:
            result.extend(self._generateRealTableCell(cell, **args))

        return result

    def _generateEndOfTableIndicator(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) indicating that this cell is the last cell
        in the table. Overridden here because Orca keeps saying "end
        of table" in certain lists (e.g. the Templates and Documents
        dialog).
        """

        if self._script.get_table_navigator().last_input_event_was_navigation_command() \
           or self._script.inSayAll():
            return []

        if AXUtilities.is_dialog_or_alert(self._script.utilities.topLevelObject(obj)):
            return []

        return super()._generateEndOfTableIndicator(obj, **args)

    def _generateNewAncestors(self, obj, **args):
        priorObj = args.get('priorObj', None)
        if not priorObj or AXObject.get_role_name(priorObj) == 'text frame':
            return []

        if self._script.utilities.isSpreadSheetCell(obj) \
           and self._script.utilities.isDocumentPanel(AXObject.get_parent(priorObj)):
            return []

        return super()._generateNewAncestors(obj, **args)

    def _generateOldAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object being left."""

        if AXObject.get_role_name(obj) == 'text frame':
            return []

        priorObj = args.get('priorObj', None)
        if self._script.utilities.isSpreadSheetCell(priorObj):
            return []

        return super()._generateOldAncestors(obj, **args)

    def _generateUnselectedCell(self, obj, **args):
        if not self._script.utilities.isGUICell(obj):
            return []

        return super()._generateUnselectedCell(obj, **args)
