#!/usr/bin/python

"""Test to verify spell checking support."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("The quuuiick brown fox"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("jumps overr the lazy dog"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F7"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "1. Enter F7 to bring up the spell checking dialog",
    ["SPEECH OUTPUT: 'Spelling: English (USA) frame'",
     "SPEECH OUTPUT: 'Misspelled word: quuuiick'",
     "SPEECH OUTPUT: 'q'",
     "SPEECH OUTPUT: 'u'",
     "SPEECH OUTPUT: 'u'",
     "SPEECH OUTPUT: 'u'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'c'",
     "SPEECH OUTPUT: 'k'",
     "SPEECH OUTPUT: 'Suggestions quick'",
     "SPEECH OUTPUT: 'q'",
     "SPEECH OUTPUT: 'u'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'c'",
     "SPEECH OUTPUT: 'k'",
     "SPEECH OUTPUT: 'Context is The quuuiick brown fox'",
     "SPEECH OUTPUT: 'Spelling: English (USA) dialog'",
     "SPEECH OUTPUT: 'Correct push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>I"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. Alt I to ignore the first error and present the next",
    ["SPEECH OUTPUT: 'Suggestions overt'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'v'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 't'"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
