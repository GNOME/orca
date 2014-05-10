#!/usr/bin/python

"""Test of presentation of indentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("   This is a test."))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow to typed line",
    ["KNOWN ISSUE: We are failing to announce indentation",
     "SPEECH OUTPUT: '		   This is a test.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
