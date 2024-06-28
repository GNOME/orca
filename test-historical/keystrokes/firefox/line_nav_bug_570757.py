#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This is a test.'",
     "     VISIBLE:  'This is a test.', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Solution'",
     "     VISIBLE:  'Solution', cursor=1",
     "SPEECH OUTPUT: 'Solution panel'",
     "SPEECH OUTPUT: 'Solution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Solution  Here is a step-by-step tutorial:'",
     "     VISIBLE:  'Solution  Here is a step-by-step', cursor=11",
     "SPEECH OUTPUT: 'Here is a step-by-step tutorial:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '• Do this thing'",
     "     VISIBLE:  '• Do this thing', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '• Do this thing.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  '• Do this other thing'",
     "     VISIBLE:  '• Do this other thing', cursor=1",
     "SPEECH OUTPUT: '• Do this other thing.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  '• Do this thing'",
     "     VISIBLE:  '• Do this thing', cursor=1",
     "SPEECH OUTPUT: '• Do this thing.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Solution  Here is a step-by-step tutorial:'",
     "     VISIBLE:  'Solution  Here is a step-by-step', cursor=11",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'Here is a step-by-step tutorial:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Solution'",
     "     VISIBLE:  'Solution', cursor=1",
     "SPEECH OUTPUT: 'Solution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'This is a test.'",
     "     VISIBLE:  'This is a test.', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
