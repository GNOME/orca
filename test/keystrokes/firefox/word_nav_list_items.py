#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=31",
     "SPEECH OUTPUT: '1. This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Next Word",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=3",
     "SPEECH OUTPUT: '1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Next Word",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=8",
     "SPEECH OUTPUT: 'This.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Next Word",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=1",
     "SPEECH OUTPUT: 'is.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Next Word",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=1",
     "SPEECH OUTPUT: 'a.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Previous Word",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=1",
     "SPEECH OUTPUT: 'a.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Previous Word",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=9",
     "SPEECH OUTPUT: 'is.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "8. Previous Word",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=4",
     "SPEECH OUTPUT: 'This.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
