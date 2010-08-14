#!/usr/bin/python

"""Test for navigating amongst table cells in Writer."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# Start oowriter. There is a table_cells.params file that will
# automatically load table-sample.odt
#
sequence.append(WaitForWindowActivate("table-sample(.odt|) - " + utils.getOOoName("Writer"),None))

######################################################################
# Type Control-Home to move the text caret to the start of the document.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# Type a down arrow to move to the next line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to move to the next line",
    ["BRAILLE LINE:  'This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=16",
     "BRAILLE LINE:  'This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=16",
     "SPEECH OUTPUT: 'This is a test.'"]))

######################################################################
# Down Arrow to move a few rows into the table.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "1. Down",
    ["BRAILLE LINE:  'table with 7 rows 7 columns'",
     "     VISIBLE:  'table with 7 rows 7 columns', cursor=0",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Mon Paragraph") + "'",
     "     VISIBLE:  'Mon Paragraph', cursor=1",
     "SPEECH OUTPUT: 'table with 7 rows 7 columns'",
     "SPEECH OUTPUT: 'Mon'",
     "SPEECH OUTPUT: 'Cell B1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell B2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "3. Down",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: 'Cell B3'"]))

######################################################################
# Toggle structural navigation
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("z"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

######################################################################
# Use table navigation to move to amongst the cells
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "1. Alt Shift Left.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 3 Paragraph") + "'",
     "     VISIBLE:  '3 Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 3, column 1.'",
     "     VISIBLE:  'Row 3, column 1.', cursor=0",
     "SPEECH OUTPUT: '3'",
     "SPEECH OUTPUT: 'Row 3, column 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Alt Shift Left.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 3 Paragraph") + "'",
     "     VISIBLE:  '3 Paragraph', cursor=1",
     "BRAILLE LINE:  'Beginning of row.'",
     "     VISIBLE:  'Beginning of row.', cursor=0",
     "SPEECH OUTPUT: 'Beginning of row.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "3. Alt Shift Right.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 3 Paragraph") + "'",
     "     VISIBLE:  '3 Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 3, column 2.'",
     "     VISIBLE:  'Row 3, column 2.', cursor=0",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: 'Row 3, column 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "4. Alt Shift Right.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 5 Paragraph") + "'",
     "     VISIBLE:  '5 Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 3, column 3.'",
     "     VISIBLE:  'Row 3, column 3.', cursor=0",
     "SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: 'Row 3, column 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "5. Alt Shift Right.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 5 Paragraph") + "'",
     "     VISIBLE:  '5 Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 6 Paragraph 7 Paragraph") + "'",
     "     VISIBLE:  '6 Paragraph 7 Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 3, column 4.'",
     "     VISIBLE:  'Row 3, column 4.', cursor=0",
     "BRAILLE LINE:  'Cell spans 2 columns'",
     "     VISIBLE:  'Cell spans 2 columns', cursor=0",
     "SPEECH OUTPUT: '6'",
     "SPEECH OUTPUT: '7'",
     "SPEECH OUTPUT: 'Row 3, column 4.'",
     "SPEECH OUTPUT: 'Cell spans 2 columns'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "6. Alt Shift Up.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table 6 Paragraph 7 Paragraph") + "'",
     "     VISIBLE:  '6 Paragraph 7 Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 2, column 4.'",
     "     VISIBLE:  'Row 2, column 4.', cursor=0",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Row 2, column 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "7. Alt Shift Up.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Wed Paragraph") + "'",
     "     VISIBLE:  'Wed Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 1, column 4.'",
     "     VISIBLE:  'Row 1, column 4.', cursor=0",
     "SPEECH OUTPUT: 'Wed'",
     "SPEECH OUTPUT: 'Row 1, column 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Alt Shift Up.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Wed Paragraph") + "'",
     "     VISIBLE:  'Wed Paragraph', cursor=1",
     "BRAILLE LINE:  'Top of column.'",
     "     VISIBLE:  'Top of column.', cursor=0",
     "SPEECH OUTPUT: 'Top of column.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>End"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "9. Alt Shift End.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Wed Paragraph") + "'",
     "     VISIBLE:  'Wed Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 7, column 7.'",
     "     VISIBLE:  'Row 7, column 7.', cursor=0",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Row 7, column 7.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Alt Shift Down.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "BRAILLE LINE:  'Bottom of column.'",
     "     VISIBLE:  'Bottom of column.', cursor=0",
     "SPEECH OUTPUT: 'Bottom of column.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Alt Shift Right.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "BRAILLE LINE:  'End of row.'",
     "     VISIBLE:  'End of row.', cursor=0",
     "SPEECH OUTPUT: 'End of row.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "12. Alt Shift Home.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Sun Paragraph") + "'",
     "     VISIBLE:  'Sun Paragraph', cursor=1",
     "BRAILLE LINE:  'Row 1, column 1.'",
     "     VISIBLE:  'Row 1, column 1.', cursor=0",
     "SPEECH OUTPUT: 'Sun'",
     "SPEECH OUTPUT: 'Row 1, column 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Alt Shift Up.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample2(.odt|)", "Calendar-1 Table Sun Paragraph") + "'",
     "     VISIBLE:  'Sun Paragraph', cursor=1",
     "BRAILLE LINE:  'Top of column.'",
     "     VISIBLE:  'Top of column.', cursor=0",
     "SPEECH OUTPUT: 'Top of column.'"]))

######################################################################
# Enter Alt-f, Alt-c to close this Writer application.
# A save dialog will appear.
#
sequence.append(KeyComboAction("<Alt><Shift>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt><Shift>c"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))

######################################################################
# Enter Alt-f, right arrow and Return, (File->New->Text Document),
# to get the application back to the state it was in when the
# test started.
#
sequence.append(KeyComboAction("<Alt><Shift>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
