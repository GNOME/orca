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
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  ' Before Line After'",
     "     VISIBLE:  ' Before Line After', cursor=1",
     "SPEECH OUTPUT: 'Before'",
     "SPEECH OUTPUT: 'Line'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'After'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'End'",
     "     VISIBLE:  'End', cursor=1",
     "SPEECH OUTPUT: 'End'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  ' Before Line After'",
     "     VISIBLE:  ' Before Line After', cursor=1",
     "SPEECH OUTPUT: 'Before'",
     "SPEECH OUTPUT: 'Line'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'After'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
