#!/usr/bin/python

"""Test of structural navigation by heading."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "1. h for next heading",
    ["BRAILLE LINE:  'line 2 h1'",
     "     VISIBLE:  'line 2 h1', cursor=1",
     "SPEECH OUTPUT: 'line 2'",
     "SPEECH OUTPUT: 'link heading level 1.'",
     "SPEECH OUTPUT: 'clickable'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
