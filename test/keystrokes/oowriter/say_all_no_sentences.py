#!/usr/bin/python

"""Test SayAll presentation in document without sentence punctuation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("The quick"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("brown"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("fox jumps over"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("the lazy dog"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. SayAll",
    ["SPEECH OUTPUT: 'The quick'",
     "SPEECH OUTPUT: 'brown'",
     "SPEECH OUTPUT: 'fox jumps over'",
     "SPEECH OUTPUT: 'the lazy dog'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
