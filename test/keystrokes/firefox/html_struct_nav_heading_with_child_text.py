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
    ["KNOWN ISSUE: We're presenting the role first because of the child text",
     "BRAILLE LINE:  'line 2'",
     "     VISIBLE:  'line 2', cursor=1",
     "SPEECH OUTPUT: 'heading level 1 line 2'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
