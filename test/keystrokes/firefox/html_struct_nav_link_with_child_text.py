#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("k"))
sequence.append(utils.AssertPresentationAction(
    "1. k for next link",
    ["BRAILLE LINE:  'line 2'",
     "     VISIBLE:  'line 2', cursor=1",
     "SPEECH OUTPUT: 'line 2'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
