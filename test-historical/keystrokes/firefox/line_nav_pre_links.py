#!/usr/bin/python

"""Test of line navigation output of Firefox."""

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
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Line 2'",
     "     VISIBLE:  'Line 2', cursor=1",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Line 4'",
     "     VISIBLE:  'Line 4', cursor=1",
     "SPEECH OUTPUT: 'Line 4'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Line 5'",
     "     VISIBLE:  'Line 5', cursor=1",
     "SPEECH OUTPUT: 'Line 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'Line 4'",
     "     VISIBLE:  'Line 4', cursor=1",
     "SPEECH OUTPUT: 'Line 4'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Line 2'",
     "     VISIBLE:  'Line 2', cursor=1",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
