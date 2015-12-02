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
    ["SPEECH OUTPUT: 'This element is not hidden.'",
     "SPEECH OUTPUT: 'This element hidden by position off screen.'",
     "SPEECH OUTPUT: 'This element is in a parent which is not hidden.'",
     "SPEECH OUTPUT: 'This element is in a parent hidden by position off screen'",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
