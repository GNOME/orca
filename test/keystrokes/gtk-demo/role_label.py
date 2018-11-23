#!/usr/bin/python

"""Test of label presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Dialog and Message Boxes"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("space"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. This message box label",
    ["BRAILLE LINE:  'This message box has been popped up the following",
     "number of times: number of times:'",
     "     VISIBLE:  'of times: number of times:', cursor=27",
     "BRAILLE LINE:  'This message box has been popped up the following",
     "number of times: number of times:'",
     "     VISIBLE:  'of times: number of times:', cursor=27",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. This message box label Where Am I",
    ["BRAILLE LINE:  'This message box has been popped up the following",
     "number of times: number of times:'",
     "     VISIBLE:  'of times: number of times:', cursor=27",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. This message box label Extended Where Am I",
    ["BRAILLE LINE:  'This message box has been popped up the following",
     "number of times: number of times:'",
     "     VISIBLE:  'of times: number of times:', cursor=27",
     "BRAILLE LINE:  'This message box has been popped up the following",
     "number of times: number of times:'",
     "     VISIBLE:  'of times: number of times:', cursor=27",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "4. Press Home to unselect the label and move to the first character'",
    ["KNOWN ISSUE: The message text is being duplicated.",
     "BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=11",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times:'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. This message box label caret movement to 'h'",
    ["BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=12",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. This message box label caret select 'his' of 'This'",
    ["BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=15",
     "SPEECH OUTPUT: 'his'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. This message box label caret selection Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=15",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. This message box label caret selection Extended Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=15",
     "BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=15",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Left Arrow to move to h unselecting his'",
    ["BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=12",
     "SPEECH OUTPUT: 'his'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "10. This message box label caret select 'T' in 'This'",
    ["BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=11",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "11. This message box label caret unselect 'T' and select rest of 'This'",
    ["BRAILLE LINE:  'gtk-demo application Information alert This message box has been popped up the following",
     "number of times: This message box has been popped up the following'",
     "     VISIBLE:  'of times: This message box has b', cursor=15",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'his'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
