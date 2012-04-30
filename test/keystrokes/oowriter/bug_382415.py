#!/usr/bin/python

"""Test to verify bug #382415 is still fixed.
   Speak cell/row setting ignored in OOo Writer tables.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_382415.params file that will
#    automatically load table-sample.odt
#
sequence.append(WaitForWindowActivate("table-sample(.odt|) - " + utils.getOOoName("Writer"), None))

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
    "Down arrow to next line",
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
    "Down arrow to move to the Mon table column header",
    ["BRAILLE LINE:  'table with 7 rows 7 columns'",
     "     VISIBLE:  'table with 7 rows 7 columns', cursor=0",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Mon Paragraph") + "'",
     "     VISIBLE:  'Mon Paragraph', cursor=1",
     "SPEECH OUTPUT: 'table with 7 rows 7 columns'",
     "SPEECH OUTPUT: 'Mon'",
     "SPEECH OUTPUT: 'Cell B1'"]))

######################################################################
# 5. Type a down arrow to move to the blank table cell on the next row.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Down arrow to move to the blank table cell on the next row",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Paragraph") + "'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell B2'"]))

######################################################################
# 6. Type a down arrow to move to the "4" table cell on the next row.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Down arrow to move to the '4' table cell on the next row",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 4 Paragraph") + "'",
     "     VISIBLE:  '4 Paragraph', cursor=1",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: 'Cell B3'"]))

######################################################################
# 7. Type a down arrow to move to the "11" table cell on the next row.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Down arrow to move to the '11' table cell on the next row",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table 11 Paragraph") + "'",
     "     VISIBLE:  '11 Paragraph', cursor=1",
     "SPEECH OUTPUT: '11'",
     "SPEECH OUTPUT: 'Cell B4'"]))

######################################################################
# 8. Enter Alt-f, Alt-c to close this Writer application.
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
# 9. Enter Alt-f, right arrow and Return, (File->New->Text Document),
#    to get the application back to the state it was in when the
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
# 10. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
