#!/usr/bin/python

"""Test for navigating amongst table cells in Writer."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# Start oowriter. There is a table_cells.params file that will
# automatically load table-sample.odt
#
sequence.append(WaitForWindowActivate("table-sample(.odt|) - " + utils.getOOoName("Writer"), None))

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
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell B2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "3. Down",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: 'Cell B3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "4. Down",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 11 Paragraph") + "'",
     "     VISIBLE:  '11 Paragraph', cursor=1",
     "SPEECH OUTPUT: '11'",
     "SPEECH OUTPUT: 'Cell B4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "5. Down",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 18 Paragraph") + "'",
     "     VISIBLE:  '18 Paragraph', cursor=1",
     "SPEECH OUTPUT: '18'",
     "SPEECH OUTPUT: 'Cell B5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "6. Down",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 25 Paragraph") + "'",
     "     VISIBLE:  '25 Paragraph', cursor=1",
     "SPEECH OUTPUT: '25'",
     "SPEECH OUTPUT: 'Cell B6'"]))

######################################################################
# Tab to move to amongst the cells
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 26 Paragraph") + "'",
     "     VISIBLE:  '26 Paragraph', cursor=1",
     "SPEECH OUTPUT: '26'",
     "SPEECH OUTPUT: 'Cell C6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 27 Paragraph") + "'",
     "     VISIBLE:  '27 Paragraph', cursor=1",
     "SPEECH OUTPUT: '27'",
     "SPEECH OUTPUT: 'Cell D6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 28 Paragraph") + "'",
     "     VISIBLE:  '28 Paragraph', cursor=1",
     "SPEECH OUTPUT: '28'",
     "SPEECH OUTPUT: 'Cell E6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 29 Paragraph") + "'",
     "     VISIBLE:  '29 Paragraph', cursor=1",
     "SPEECH OUTPUT: '29'",
     "SPEECH OUTPUT: 'Cell F6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 30 Paragraph") + "'",
     "     VISIBLE:  '30 Paragraph', cursor=1",
     "SPEECH OUTPUT: '30'",
     "SPEECH OUTPUT: 'Cell G6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 31 Paragraph") + "'",
     "     VISIBLE:  '31 Paragraph', cursor=1",
     "SPEECH OUTPUT: '31'",
     "SPEECH OUTPUT: 'Cell A7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "7. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell B7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "8. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell C7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "9. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell D7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "10. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell E7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "11. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell F7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "12. Tab to the next cell.",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'End of table blank'",
     "SPEECH OUTPUT: 'Cell G7'"]))

######################################################################
# Arrow Left and Right from the last cell.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell F7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Right",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'End of table blank'",
     "SPEECH OUTPUT: 'Cell G7'"]))

######################################################################
# Arrow Up and Down from  the last cell. The repeat with row reading
# enabled.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Up - Speak Cell",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 30 Paragraph") + "'",
     "     VISIBLE:  '30 Paragraph', cursor=1",
     "SPEECH OUTPUT: '30'",
     "SPEECH OUTPUT: 'Cell G6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Down - Speak Cell",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'End of table blank'",
     "SPEECH OUTPUT: 'Cell G7'"]))

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Up - Speak Row",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 24 25 26 27 28 29 30") + "'",
     "     VISIBLE:  '30', cursor=1",
     "SPEECH OUTPUT: '24 25 26 27 28 29 30'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Down - Speak Row",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 31") + "      '",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'End of table 31'"]))

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

######################################################################
# Enter Alt-f, Alt-c to close this Writer application.
# A save dialog will appear.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
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
sequence.append(KeyComboAction("<Alt>f"))
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
