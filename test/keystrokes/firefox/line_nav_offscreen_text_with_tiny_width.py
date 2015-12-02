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
    ["KNOWN ISSUE: This should be a single line, but Gecko tells us it is not because of CSS",
     "BRAILLE LINE:  'This'",
     "     VISIBLE:  'This', cursor=1",
     "SPEECH OUTPUT: 'This'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'should'",
     "     VISIBLE:  'should', cursor=1",
     "SPEECH OUTPUT: 'should'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'all'",
     "     VISIBLE:  'all', cursor=1",
     "SPEECH OUTPUT: 'all'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'should'",
     "     VISIBLE:  'should', cursor=1",
     "SPEECH OUTPUT: 'should'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'This'",
     "     VISIBLE:  'This', cursor=1",
     "SPEECH OUTPUT: 'This'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
