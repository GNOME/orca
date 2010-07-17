#!/usr/bin/python

"""Test to verify bug #356334 is still fixed.
   readCharAttributes crashes OOo Calc 2.0.4 RC1.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oocalc. There is a bug_356334.params file that will
#    automatically load fruit.ods.
#
sequence.append(PauseAction(3000))

######################################################################
# 2. Type Control-Home to position the text caret in cell A1.
#
sequence.append(KeyComboAction("<Control>Home"))

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
# 4. Type Insert-f to get text attributes on the current cell (A2).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Type Insert-f to get text attributes on the current cell (A2)",
    ["SPEECH OUTPUT: 'size 16'",
     "SPEECH OUTPUT: 'family name Arial'",
     "SPEECH OUTPUT: 'bold'",
     "SPEECH OUTPUT: 'style italic'"]))

######################################################################
# 5. Press the right arrow to move to cell B2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Press the right arrow to move to cell B2",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Yes Cell B2 '",
     "     VISIBLE:  'Yes Cell B2 ', cursor=1",
     "SPEECH OUTPUT: 'Yes B2'"]))

######################################################################
# 6. Type Insert-f to get text attributes on the current cell (B2).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Type Insert-f to get text attributes on the current cell (B2)",
    ["SPEECH OUTPUT: 'size 10'",
     "SPEECH OUTPUT: 'family name Arial'"]))

######################################################################
# 7. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
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
# 8. Enter Alt-f, right arrow, down arrow and Return,
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
# 8. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
