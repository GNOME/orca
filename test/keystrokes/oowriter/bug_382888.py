#!/usr/bin/python

"""Test to verify bug #382888 is still fixed.
   Orca should announce when you cross a cell boundary in OOo Writer tables.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_382888.params file that will
#    automatically load table-sample.odt
#
sequence.append(WaitForWindowActivate("table-sample(.odt|) - " + utils.getOOoName("Writer"),None))

######################################################################
# 2. Type Control-Home to move the text caret to the start of the document.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Type a down arrow to move to the next line.
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
# 4. Type a down arrow to move to the Mon table column header.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to move to the Mon table column header",
    ["BRAILLE LINE:  'table with 7 rows 7 columns'",
     "     VISIBLE:  'table with 7 rows 7 columns', cursor=0",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Mon Paragraph") + "'",
     "     VISIBLE:  'Mon Paragraph', cursor=1",
     "SPEECH OUTPUT: 'table with 7 rows 7 columns'",
     "SPEECH OUTPUT: 'Mon'",
     "SPEECH OUTPUT: 'Cell B1'"]))

######################################################################
# 5. Type a Tab to move to the Tue table column header.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a Tab to move to the Tue table column header",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Tue Paragraph") + "'",
     "     VISIBLE:  'Tue Paragraph', cursor=1",
     "SPEECH OUTPUT: 'Tue'",
     "SPEECH OUTPUT: 'Cell C1'"]))

######################################################################
# 6. Type a down arrow to move to the blank cell C2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to move to the blank cell C2",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell C2'"]))

######################################################################
# 7. Type a down arrow to move to cell C3 containing "5".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to move to cell C3 containing '5'",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 5 Paragraph") + "'",
     "     VISIBLE:  '5 Paragraph', cursor=1",
     "SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: 'Cell C3'"]))

######################################################################
# 8. Type a Shift-Tab to move to cell B3 containing "4".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a Shift-Tab to move to cell B3 containing '4'",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: 'Cell B3'"]))

######################################################################
# 9. Type a down arrow to move to cell B4 containing "11".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to move to cell B4 containing '11'",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 11 Paragraph") + "'",
     "     VISIBLE:  '11 Paragraph', cursor=1",
     "SPEECH OUTPUT: '11'",
     "SPEECH OUTPUT: 'Cell B4'"]))

######################################################################
# 10. Type an up arrow to move to cell B3 containing "4".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type an up arrow to move to cell B3 containing '4'",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: 'Cell B3'"]))

######################################################################
# 11. Enter Alt-f, Alt-c to close this Writer application.
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
# 12. Enter Alt-f, right arrow and Return, (File->New->Text Document),
#     to get the application back to the state it was in when the
#    test started.
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
# 13. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
