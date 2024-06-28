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
    ["SPEECH OUTPUT: 'Start of test'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line four'",
     "SPEECH OUTPUT: 'Line five'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line four'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line five'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Line one'",
     "SPEECH OUTPUT: 'Line two'",
     "SPEECH OUTPUT: 'Click me'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
