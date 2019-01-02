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

import pyatspi

import orca.messages as messages
import orca.settings_manager as settings_manager
import orca.speech_generator as speech_generator

_settingsManager = settings_manager.getManager()

class SpeechGenerator(speech_generator.SpeechGenerator):
    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def __overrideParagraph(self, obj, **args):
        # Treat a paragraph which is serving as a text entry in a dialog
        # as a text object.
        #
        role = args.get('role', obj.getRole())
        override = \
            role == "text frame" \
            or (role == pyatspi.ROLE_PARAGRAPH \
                and self._script.utilities.ancestorWithRole(
                      obj, [pyatspi.ROLE_DIALOG], [pyatspi.ROLE_APPLICATION]))
        return override

    def _generateRoleName(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_TOGGLE_BUTTON \
           and obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            pass
        else:
            # Treat a paragraph which is serving as a text entry in a dialog
            # as a text object.
            #
            override = self.__overrideParagraph(obj, **args)
            if override:
                oldRole = self._overrideRole(pyatspi.ROLE_TEXT, args)
            # Treat a paragraph which is inside of a spreadsheet cell as
            # a spreadsheet cell.
            #
            elif role == 'ROLE_SPREADSHEET_CELL':
                oldRole = self._overrideRole(pyatspi.ROLE_TABLE_CELL, args)
                override = True
            result.extend(speech_generator.SpeechGenerator._generateRoleName(
                          self, obj, **args))
            if override:
                self._restoreRole(oldRole, args)
        return result

    def _generateTextRole(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_TEXT and obj.parent.getRole() == pyatspi.ROLE_COMBO_BOX:
            return []

        if role != pyatspi.ROLE_PARAGRAPH \
           or self.__overrideParagraph(obj, **args):
            result.extend(self._generateRoleName(obj, **args))
        return result

    def _generateLabel(self, obj, **args):
        """Returns the label for an object as an array of strings (and
        possibly voice and audio specifications).  The label is
        determined by the displayedLabel method of the script utility,
        and an empty array will be returned if no label can be found.
        """
        result = []
        acss = self.voice(speech_generator.DEFAULT)
        override = self.__overrideParagraph(obj, **args)
        label = self._script.utilities.displayedLabel(obj) or ""
        if not label and override:
            label = self._script.utilities.displayedLabel(obj.parent) or ""
        if label:
            result.append(label.strip())
            result.extend(acss)
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
        if obj.name:
            result = [obj.name]
            result.extend(self.voice(speech_generator.DEFAULT))
            return result

        return super()._generateName(obj, **args)

    def _generateLabelAndName(self, obj, **args):
        if obj.getRole() != pyatspi.ROLE_COMBO_BOX:
            return super()._generateLabelAndName(obj, **args)

        # TODO - JD: This should be the behavior by default because many
        # toolkits use the label for the name.
        result = []
        label = self._script.utilities.displayedLabel(obj) or obj.name
        if label:
            result.append(label)
            result.extend(self.voice(speech_generator.DEFAULT))           

        name = obj.name
        if label == name or not name:
            selected = self._script.utilities.selectedChildren(obj)
            if selected:
                name = selected[0].name

        if name:
            result.append(name)
            result.extend(self.voice(speech_generator.DEFAULT))

        return result

    def _generateLabelOrName(self, obj, **args):
        """Gets the label or the name if the label is not preset."""

        result = []
        acss = self.voice(speech_generator.DEFAULT)
        override = self.__overrideParagraph(obj, **args)
        # Treat a paragraph which is serving as a text entry in a dialog
        # as a text object.
        #
        if override:
            result.extend(self._generateLabel(obj, **args))
            if len(result) == 0 and obj.parent:
                parentLabel = self._generateLabel(obj.parent, **args)
                # If we aren't already focused, we will have spoken the
                # parent as part of the speech context and do not want
                # to repeat it.
                #
                alreadyFocused = args.get('alreadyFocused', False)
                if alreadyFocused:
                    result.extend(parentLabel)
                # If we still don't have a label, look to the name.
                #
                if not parentLabel and obj.name and len(obj.name):
                    result.append(obj.name)
                if result:
                    result.extend(acss)
        else:
            result.extend(speech_generator.SpeechGenerator._generateLabelOrName(
                self, obj, **args))
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
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not _settingsManager.getSetting('speakDescription'):
            return []

        if not args.get('formatType', '').endswith('WhereAmI'):
            return []

        result = []
        acss = self.voice(speech_generator.SYSTEM)
        if obj.description:
            # The description of some OOo paragraphs consists of the name
            # and the displayed text, with punctuation added. Try to spot
            # this and, if found, ignore the description.
            #
            text = self._script.utilities.displayedText(obj) or ""
            desc = obj.description.replace(text, "")
            for item in obj.name.split():
                desc = desc.replace(item, "")
            for char in desc.strip():
                if char.isalnum():
                    result.append(obj.description)
                    break

        if result:
            result.extend(acss)
        return result

    def _generateCurrentLineText(self, obj, **args):
        if self._script.utilities.isTextDocumentCell(obj.parent):
            priorObj = args.get('priorObj', None)
            if priorObj and priorObj.parent != obj.parent:
                return []

        if obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            entry = self._script.utilities.getEntryForEditableComboBox(obj)
            if entry:
                return super()._generateCurrentLineText(entry)
            return []

        # TODO - JD: The SayLine, etc. code should be generated and not put
        # together in the scripts. In addition, the voice crap needs to go
        # here. Then it needs to be removed from the scripts.
        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        voice = self.voice(string=text)
        text = self._script.utilities.adjustForLinks(obj, text, startOffset)
        text = self._script.utilities.adjustForRepeats(text)
        if not text:
            result = [messages.BLANK]
        else:
            result = [text]
        result.extend(voice)

        return result

    def _generateToggleState(self, obj, **args):
        """Treat toggle buttons in the toolbar specially. This is so we can
        have more natural sounding speech such as "bold on", "bold off", etc."""
        acss = self.voice(speech_generator.SYSTEM)
        result = []
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_TOGGLE_BUTTON \
           and obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            if obj.getState().contains(pyatspi.STATE_CHECKED):
                result.append(messages.ON)
            else:
                result.append(messages.OFF)
            result.extend(acss)
        elif role == pyatspi.ROLE_TOGGLE_BUTTON:
            result.extend(speech_generator.SpeechGenerator._generateToggleState(
                self, obj, **args))
        return result

    def _generateRowHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the row header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned. Overridden here so that we can get the dynamic
        row header(s).
        """

        if self._script.utilities.shouldReadFullRow(obj):
            return []

        newOnly = args.get('newOnly', False)
        rowHeader, columnHeader = \
            self._script.utilities.getDynamicHeadersForCell(obj, newOnly)
        if not rowHeader:
            return super()._generateRowHeader(obj, **args)

        result = []
        text = self._script.utilities.displayedText(rowHeader)
        if text:
            result.append(text)
            result.extend(self.voice(speech_generator.DEFAULT))

        return result

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned. Overridden here so that we can get the dynamic
        column header(s).
        """

        newOnly = args.get('newOnly', False)
        rowHeader, columnHeader = \
            self._script.utilities.getDynamicHeadersForCell(obj, newOnly)
        if not columnHeader:
            return super()._generateColumnHeader(obj, **args)

        result = []
        text = self._script.utilities.displayedText(columnHeader)
        if text:
            result.append(text)
            result.extend(self.voice(speech_generator.DEFAULT))

        return result

    def _generateTooLong(self, obj, **args):
        """If there is text in this spread sheet cell, compare the size of
        the text within the table cell with the size of the actual table
        cell and report back to the user if it is larger.

        Returns an indication of how many characters are greater than the size
        of the spread sheet cell, or None if the message fits.
        """
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(speech_generator.SYSTEM)
        try:
            text = obj.queryText()
            objectText = \
                self._script.utilities.substring(obj, 0, -1)
            extents = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
        except NotImplementedError:
            pass
        else:
            tooLongCount = 0
            for i in range(0, len(objectText)):
                [x, y, width, height] = text.getRangeExtents(i, i + 1, 0)
                if x < extents.x:
                    tooLongCount += 1
                elif (x + width) > extents.x + extents.width:
                    tooLongCount += len(objectText) - i
                    break
            if tooLongCount > 0:
                result = [messages.charactersTooLong(tooLongCount)]
        if result:
            result.extend(acss)
        return result

    def _generateHasFormula(self, obj, **args):
        inputLine = self._script.utilities.locateInputLine(obj)
        if not inputLine:
            return []

        text = self._script.utilities.displayedText(inputLine)
        if text and text.startswith("="):
            result = [messages.HAS_FORMULA]
            result.extend(self.voice(speech_generator.SYSTEM))
            return result

        return []

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
            if self._script._lastCommandWasStructNav:
                return result

            if _settingsManager.getSetting('speakCellCoordinates'):
                result.append(obj.name)
            return result

        isBasicWhereAmI = args.get('formatType') == 'basicWhereAmI'
        speakCoordinates = _settingsManager.getSetting('speakSpreadsheetCoordinates')
        if speakCoordinates and not isBasicWhereAmI:
            result.append(self._script.utilities.spreadSheetCellName(obj))

        if self._script.utilities.shouldReadFullRow(obj):
            row, col, table = self._script.utilities.getRowColumnAndTable(obj)
            lastRow = self._script.pointOfReference.get("lastRow")
            if row != lastRow:
                return result

        tooLong = self._generateTooLong(obj, **args)
        if tooLong:
            result.extend(self._generatePause(obj, **args))
            result.extend(tooLong)

        hasFormula = self._generateHasFormula(obj, **args)
        if hasFormula:
            result.extend(self._generatePause(obj, **args))
            result.extend(hasFormula)

        return result

    def _generateTableCellRow(self, obj, **args):
        if not self._script.utilities.shouldReadFullRow(obj):
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

        if self._script._lastCommandWasStructNav or self._script.inSayAll():
            return []

        topLevel = self._script.utilities.topLevelObject(obj)
        if topLevel and topLevel.getRole() == pyatspi.ROLE_DIALOG:
            return []

        return super()._generateEndOfTableIndicator(obj, **args)

    def _generateNewAncestors(self, obj, **args):
        priorObj = args.get('priorObj', None)
        if not priorObj or priorObj.getRoleName() == 'text frame':
            return []

        if self._script.utilities.isSpreadSheetCell(obj) \
           and self._script.utilities.isDocumentPanel(priorObj.parent):
            return []

        return super()._generateNewAncestors(obj, **args)

    def _generateOldAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object being left."""

        if obj.getRoleName() == 'text frame':
            return []

        priorObj = args.get('priorObj', None)
        if self._script.utilities.isSpreadSheetCell(priorObj):
            return []

        return super()._generateOldAncestors(obj, **args)

    def _generateUnselectedCell(self, obj, **args):
        if self._script.utilities.isSpreadSheetCell(obj):
            return []

        if self._script._lastCommandWasStructNav:
            return []

        return super()._generateUnselectedCell(obj, **args)

    def generateSpeech(self, obj, **args):
        result = []
        if args.get('formatType', 'unfocused') == 'basicWhereAmI' \
           and self._script.utilities.isSpreadSheetCell(obj):
            oldRole = self._overrideRole('ROLE_SPREADSHEET_CELL', args)
            # In addition, if focus is in a cell being edited, we cannot
            # query the accessible table interface for coordinates and the
            # like because we're temporarily in an entirely different object
            # which is outside of the table. This makes things difficult.
            # However, odds are that if we're doing a whereAmI in a cell
            # which we are editing, we have some pointOfReference info
            # we can use to guess the coordinates.
            #
            args['guessCoordinates'] = obj.getRole() == pyatspi.ROLE_PARAGRAPH
            result.extend(super().generateSpeech(obj, **args))
            del args['guessCoordinates']
            self._restoreRole(oldRole, args)
        else:
            oldRole = self._overrideRole(self._getAlternativeRole(obj, **args), args)
            result.extend(super().generateSpeech(obj, **args))
            self._restoreRole(oldRole, args)

        return result
