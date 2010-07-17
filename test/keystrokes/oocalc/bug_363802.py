#!/usr/bin/python

"""Test to verify bug #363802 is still fixed.
   When navigating in Calc from cell to cell, Orca should not say "cell".
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oocalc. There is a bug_363802.params file that will
#    automatically load fruit.ods.
#
sequence.append(PauseAction(3000))

######################################################################
# 2. Type Control-Home to position the text caret in cell A1.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Type Control-Home to position the text caret in cell A1",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '",
     "     VISIBLE:  'Cell A1 ', cursor=1",
     "SPEECH OUTPUT: 'A1'"]))

######################################################################
# 3. Press the down arrow to move to cell A2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Press the down arrow to move to cell A2",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Good in Pies Cell A2 '",
     "     VISIBLE:  'Good in Pies Cell A2 ', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies A2'"]))

######################################################################
# 4. Press the right arrow to move to cell B2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Press the right arrow to move to cell B2",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Yes Cell B2 '",
     "     VISIBLE:  'Yes Cell B2 ', cursor=1", 
     "SPEECH OUTPUT: 'Yes B2'"]))

######################################################################
# 5. Press the down arrow to move to cell B3.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Press the down arrow to move to cell B3",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Yes Cell B3 '",
     "     VISIBLE:  'Yes Cell B3 ', cursor=1", 
     "SPEECH OUTPUT: 'Yes B3'"]))

######################################################################
# 6. Press the right arrow to move to cell C3.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Press the right arrow to move to cell C3",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Yes Cell C3 '",
     "     VISIBLE:  'Yes Cell C3 ', cursor=1",
     "SPEECH OUTPUT: 'Yes C3'"]))

######################################################################
# 7. Press the up arrow to move to cell C2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Press the up arrow to move to cell C2",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table No Cell C2 '",
     "     VISIBLE:  'No Cell C2 ', cursor=1",
     "SPEECH OUTPUT: 'No C2'"]))

######################################################################
# 8. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
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
# 9. Enter Alt-f, right arrow, down arrow and Return,
#    (File->New->Spreadsheet), to get the application back 
#    to the state it was in when the test started.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Spreadsheet", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))

######################################################################
# 10. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
