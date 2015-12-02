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
    ["SPEECH OUTPUT: 'Hello world'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ', this is a test.'",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Bar'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'The end.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
