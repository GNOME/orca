#!/usr/bin/python

"""Test to verify bug #435852 is still fixed.
   Orca and OpenOffice Calc have a memory lovefest.
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

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Untitled 2 - " + utils.getOOoName("Calc"), None))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))

######################################################################
# 3. Type Control-Home to position the text caret in cell A1.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 4. Enter right arrow to move to cell B1.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Enter right arrow to move to cell B1",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell B1 '",
     "     VISIBLE:  'Cell B1 ', cursor=1",
     "SPEECH OUTPUT: 'B1'"]))

######################################################################
# 5. Enter down arrow to move to cell B2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Enter down arrow to move to cell B2",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell B2 '",
     "     VISIBLE:  'Cell B2 ', cursor=1",
     "SPEECH OUTPUT: 'B2'"]))

######################################################################
# 6. Enter left arrow to move to cell A2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Enter left arrow to move to cell A2",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A2 '",
     "     VISIBLE:  'Cell A2 ', cursor=1",
     "SPEECH OUTPUT: 'A2'"]))

######################################################################
# 7. Enter up arrow to move to cell A1.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Enter up arrow to move to cell A1",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Calc") + " Frame Untitled 2 - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '",
     "     VISIBLE:  'Cell A1 ', cursor=1",
     "SPEECH OUTPUT: 'A1'"]))

######################################################################
# 8. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Calc"), None))

######################################################################
# 9. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
