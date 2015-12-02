#!/usr/bin/python

"""Test of ARIA progressbar presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()
#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(5000))
sequence.append(utils.AssertPresentationAction(
    "1. Progress output",
    ["SPEECH OUTPUT: '10 percent.'",
     "SPEECH OUTPUT: '20 percent.'",
     "SPEECH OUTPUT: '30 percent.'",
     "SPEECH OUTPUT: '40 percent.'",
     "SPEECH OUTPUT: '50 percent.'",
     "SPEECH OUTPUT: '60 percent.'",
     "SPEECH OUTPUT: '70 percent.'",
     "SPEECH OUTPUT: '80 percent.'",
     "SPEECH OUTPUT: '90 percent.'",
     "SPEECH OUTPUT: '100 percent.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
