#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Line 1'",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'Line 3'",
     "SPEECH OUTPUT: 'Close'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line 4'",
     "SPEECH OUTPUT: 'Line 5'",
     "SPEECH OUTPUT: 'Line 6'",
     "SPEECH OUTPUT: 'Line 7'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
