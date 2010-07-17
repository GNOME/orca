#!/usr/bin/python

"""Test to verify bug #363804 is still fixed.
   Add ability to turn off coordinate announcement when navigating in Calc.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# Start oocalc. There is a bug_361167.params file that will
# automatically load fruit.ods.
#
sequence.append(PauseAction(3000))

######################################################################
# Type Control-Home to position the text caret in cell A1.
#
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

######################################################################
# Press the down arrow to move to cell A2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to A2 - don't speak cell coordinates",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Good in Pies Cell A2 '",
     "     VISIBLE:  'Good in Pies Cell A2 ', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies.'"]))

######################################################################
# Press the right arrow to move to cell B2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right to B2 - don't speak cell coordinates",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Yes Cell B2 '",
     "     VISIBLE:  'Yes Cell B2 ', cursor=1",
     "SPEECH OUTPUT: 'Yes.'"]))

######################################################################
# Type Control-Home to position the text caret in cell A1.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Control+Home to A1 - don't speak cell coordinates",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '",
     "     VISIBLE:  'Cell A1 ', cursor=1",
     "SPEECH OUTPUT: 'blank.'"]))

######################################################################
# Enter Alt-f, Alt-c to close the Calc spreadsheet window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))
#sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PANEL))

######################################################################
# Enter Alt-f, right arrow, down arrow and Return,
# (File->New->Spreadsheet), to get the application back
# to the state it was in when the test started.
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
# Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
