#!/usr/bin/python

"""Test of drawing area output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Drawing Area"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Flat review current line",
    ["BRAILLE LINE:  'Checkerboard pattern $l'",
     "     VISIBLE:  'Checkerboard pattern $l', cursor=1",
     "SPEECH OUTPUT: 'Checkerboard pattern'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "2. Flat review next line",
    ["BRAILLE LINE:  'drawing area $l'",
     "     VISIBLE:  'drawing area $l', cursor=1",
     "SPEECH OUTPUT: 'drawing area'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
