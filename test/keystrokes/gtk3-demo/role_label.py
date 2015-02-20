#!/usr/bin/python

"""Test of label presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Dialog and Message Boxes"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("space"))
sequence.append(KeyComboAction("space"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. This message box label",
    ["BRAILLE LINE:  'number of times:'",
     "     VISIBLE:  'number of times:', cursor=17",
     "BRAILLE LINE:  'number of times:'",
     "     VISIBLE:  'number of times:', cursor=17",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. This message box label Where Am I",
    ["BRAILLE LINE:  'number of times:'",
     "     VISIBLE:  'number of times:', cursor=17",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. This message box label Extended Where Am I",
    ["BRAILLE LINE:  'number of times:'",
     "     VISIBLE:  'number of times:', cursor=17",
     "BRAILLE LINE:  'number of times:'",
     "     VISIBLE:  'number of times:', cursor=17",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "4. Press Home to unselect the label and move to the first character'",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=1",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times:'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. This message box label caret movement to 'h'",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. This message box label caret select 'his' of 'This'",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=5",
     "SPEECH OUTPUT: 'his'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. This message box label caret selection Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=5",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. This message box label caret selection Extended Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=5",
     "BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=5",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Left Arrow to move to h unselecting his'",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=2",
     "BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=2",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'his'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "10. This message box label caret select 'T' in 'This'",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=1",
     "SPEECH OUTPUT: 'T' voice=uppercase",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "11. This message box label caret unselect 'T' and select rest of 'This'",
    ["BRAILLE LINE:  'gtk3-demo application Information alert This message box has been popped up the following'",
     "     VISIBLE:  'This message box has been popped', cursor=5",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'his'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
