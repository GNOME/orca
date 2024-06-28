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
    ["SPEECH OUTPUT: 'Here are some links'",
     "SPEECH OUTPUT: 'HTML Tags'",
     "SPEECH OUTPUT: '<!-->'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '<!DOCTYPE>'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '<a>'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '<abbr>'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '<acronym>'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
