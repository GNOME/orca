#!/usr/bin/python

"""Test of structural navigation by heading."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "1. h for next heading",
    ["KNOWN ISSUE: We're not speaking the initial letter",
     "BRAILLE LINE:  'line 2 h1'",
     "     VISIBLE:  'line 2 h1', cursor=1",
     "SPEECH OUTPUT: 'ine 2'",
     "SPEECH OUTPUT: 'link heading level 1 clickable'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
