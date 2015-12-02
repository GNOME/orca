#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(PauseAction(3000))

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
    ["BRAILLE LINE:  'Facebook Twitter Google+'",
     "     VISIBLE:  'Facebook Twitter Google+', cursor=1",
     "SPEECH OUTPUT: 'Facebook link.'",
     "SPEECH OUTPUT: 'Twitter link.'",
     "SPEECH OUTPUT: 'Google+ link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'line 3'",
     "     VISIBLE:  'line 3', cursor=1",
     "SPEECH OUTPUT: 'line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'Facebook Twitter Google+'",
     "     VISIBLE:  'Facebook Twitter Google+', cursor=1",
     "SPEECH OUTPUT: 'Facebook link.'",
     "SPEECH OUTPUT: 'Twitter link.'",
     "SPEECH OUTPUT: 'Google+ link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'line 1'",
     "     VISIBLE:  'line 1', cursor=1",
     "SPEECH OUTPUT: 'line 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
