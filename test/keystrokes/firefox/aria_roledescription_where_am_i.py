#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Basic Where Am I on a div with only a roledescription",
    ["BRAILLE LINE:  'Focus me 2 kill switch'",
     "     VISIBLE:  'Focus me 2 kill switch', cursor=1",
     "SPEECH OUTPUT: 'Focus me 2 kill switch'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I on a div with role button and a roledescription",
    ["BRAILLE LINE:  'Focus me 4 kill switch'",
     "     VISIBLE:  'Focus me 4 kill switch', cursor=1",
     "SPEECH OUTPUT: 'Focus me 4 kill switch'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I on a button element with a roledescription",
    ["BRAILLE LINE:  'Focus me 6 kill switch'",
     "     VISIBLE:  'Focus me 6 kill switch', cursor=1",
     "SPEECH OUTPUT: 'Focus me 6 kill switch'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
