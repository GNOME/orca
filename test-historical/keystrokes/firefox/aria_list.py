#!/usr/bin/python

"""Test of presentation of ARIA role list."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow",
    ["BRAILLE LINE:  'cat'",
     "     VISIBLE:  'cat', cursor=1",
     "SPEECH OUTPUT: 'cat.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["BRAILLE LINE:  'sparrow'",
     "     VISIBLE:  'sparrow', cursor=1",
     "SPEECH OUTPUT: 'sparrow.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic whereAmI",
    ["BRAILLE LINE:  'sparrow'",
     "     VISIBLE:  'sparrow', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: 'sparrow.'",
     "SPEECH OUTPUT: '3 of 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow",
    ["BRAILLE LINE:  'cat'",
     "     VISIBLE:  'cat', cursor=1",
     "SPEECH OUTPUT: 'cat.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
