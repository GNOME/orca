#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  '1. item'",
     "     VISIBLE:  '1. item', cursor=1",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '1. item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  '2. item'",
     "     VISIBLE:  '2. item', cursor=1",
     "SPEECH OUTPUT: '2.'",
     "SPEECH OUTPUT: 'item'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'not item'",
     "     VISIBLE:  'not item', cursor=1",
     "SPEECH OUTPUT: 'not item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '3. item'",
     "     VISIBLE:  '3. item', cursor=1",
     "SPEECH OUTPUT: '3. item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'not item'",
     "     VISIBLE:  'not item', cursor=1",
     "SPEECH OUTPUT: 'not item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  '2. item'",
     "     VISIBLE:  '2. item', cursor=1",
     "SPEECH OUTPUT: '2.'",
     "SPEECH OUTPUT: 'item'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  '1. item'",
     "     VISIBLE:  '1. item', cursor=1",
     "SPEECH OUTPUT: '1. item.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
