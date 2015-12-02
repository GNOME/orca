#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'line 1'",
     "     VISIBLE:  'line 1', cursor=1",
     "SPEECH OUTPUT: 'line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'line 2'",
     "     VISIBLE:  'line 2', cursor=1",
     "SPEECH OUTPUT: 'line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  'line 1'",
     "     VISIBLE:  'line 1', cursor=1",
     "SPEECH OUTPUT: 'line 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
