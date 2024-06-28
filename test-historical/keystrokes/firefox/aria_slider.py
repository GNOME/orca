#!/usr/bin/python

"""Test of ARIA slider presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. tab to slider",
    ["BRAILLE LINE:  'My slider 10% horizontal slider'",
     "     VISIBLE:  'My slider 10% horizontal slider', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'My slider horizontal slider 10%'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. basic whereAmI",
    ["BRAILLE LINE:  'My slider 10% horizontal slider'",
     "     VISIBLE:  'My slider 10% horizontal slider', cursor=1",
     "BRAILLE LINE:  'My slider 10% horizontal slider'",
     "     VISIBLE:  'My slider 10% horizontal slider', cursor=1",
     "SPEECH OUTPUT: 'My slider horizontal slider 10% 10 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. move slider right",
    ["BRAILLE LINE:  'My slider $15.00 horizontal slider'",
     "     VISIBLE:  'My slider $15.00 horizontal slid', cursor=1",
     "SPEECH OUTPUT: '$15.00'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. move slider right",
    ["BRAILLE LINE:  'My slider $20.00 horizontal slider'",
     "     VISIBLE:  'My slider $20.00 horizontal slid', cursor=1",
     "SPEECH OUTPUT: '$20.00'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. move slider left",
    ["BRAILLE LINE:  'My slider $15.00 horizontal slider'",
     "     VISIBLE:  'My slider $15.00 horizontal slid', cursor=1",
     "SPEECH OUTPUT: '$15.00'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "6. move slider end",
    ["BRAILLE LINE:  'My slider $100.00 horizontal slider'",
     "     VISIBLE:  'My slider $100.00 horizontal sli', cursor=1",
     "SPEECH OUTPUT: '$100.00'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "7. move slider home",
    ["BRAILLE LINE:  'My slider $0.00 horizontal slider'",
     "     VISIBLE:  'My slider $0.00 horizontal slide', cursor=1",
     "SPEECH OUTPUT: '$0.00'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
