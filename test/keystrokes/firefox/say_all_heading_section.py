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
    ["SPEECH OUTPUT: 'Heading 1.'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'Heading 2.'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'sect 1'",
     "SPEECH OUTPUT: 'Heading 3.'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'sect 2'",
     "SPEECH OUTPUT: 'Heading 4.'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'sect 3'",
     "SPEECH OUTPUT: 'Heading 5.'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'Heading 6.'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
