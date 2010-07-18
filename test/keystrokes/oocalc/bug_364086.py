#!/usr/bin/python

"""Test to verify bug #364086 is still fixed.
   Orca reports "paragraph 0 paragraph" <char> when you begin typing 
   in a Calc cell.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oocalc.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Calc"), None))

######################################################################
# 2. Enter Alt-f, right arrow, down arrow and Return.
#    (File->New->Spreadsheet).
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Spreadsheet", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "File->New->Spreadsheet",
    ["KNOWN ISSUE - OOo Calc doesn't initially emit any events to tell us which cell has focus",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame'",
     "     VISIBLE:  'Untitled 2 - " + utils.getOOoName("Calc") + " (Frame|)', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table'",
     "     VISIBLE:  'Sheet Sheet1 Table', cursor=1",
     "SPEECH OUTPUT: 'Untitled 2 - " + utils.getOOoName("Calc") + " frame'",
     "SPEECH OUTPUT: 'Sheet Sheet1 table'"]))

######################################################################
# 3. Type "hello" (without the quotes), followed by Return.
#
sequence.append(TypeAction("hello"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "Type 'hello' (without the quotes), followed by Return",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table'",
     "     VISIBLE:  'Sheet Sheet1 Table', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '",
     "     VISIBLE:  'Cell A1 ', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A2 '",
     "     VISIBLE:  'Cell A2 ', cursor=1",
     "SPEECH OUTPUT: 'Sheet Sheet1 table'",
     "SPEECH OUTPUT: 'A1'",
     "SPEECH OUTPUT: 'A2'"]))

######################################################################
# 4. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 5. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# 6. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
