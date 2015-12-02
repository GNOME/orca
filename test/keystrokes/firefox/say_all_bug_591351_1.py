#!/usr/bin/python

"""Test of sayAll output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Hello world.'",
     "SPEECH OUTPUT: 'I wonder what a bevezeto is.'",
     "SPEECH OUTPUT: 'I should Google that.'",
     "SPEECH OUTPUT: 'Aha! It is the Hungarian word for \"Introduction\".'",
     "SPEECH OUTPUT: 'Here is some'",
     "SPEECH OUTPUT: 'proof'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '.'",
     "SPEECH OUTPUT: 'I really think we need to get Attila to teach the Orca team some Hungarian.'",
     "SPEECH OUTPUT: 'Maybe one (really easy) phrase per bug comment.'",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
