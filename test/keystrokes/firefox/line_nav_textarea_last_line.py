#!/usr/bin/python

"""Test of line navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("hello world"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("goodbye world"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up",
    ["BRAILLE LINE:  'Label hello world $l'",
     "     VISIBLE:  'Label hello world $l', cursor=18",
     "SPEECH OUTPUT: 'hello world'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  'Label goodbye world $l'",
     "     VISIBLE:  'Label goodbye world $l', cursor=20",
     "SPEECH OUTPUT: 'goodbye world'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
