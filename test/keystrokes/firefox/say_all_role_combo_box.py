#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Severity'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ': Severity normal combo box'",
     "SPEECH OUTPUT: 'Priority'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ': Normal combo box'",
     "SPEECH OUTPUT: 'Resolution: ",
     "'",
     "SPEECH OUTPUT: 'FIXED'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'Version'",
     "SPEECH OUTPUT: '2.16 combo box'",
     "SPEECH OUTPUT: 'Component'",
     "SPEECH OUTPUT: 'Speech combo box'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
