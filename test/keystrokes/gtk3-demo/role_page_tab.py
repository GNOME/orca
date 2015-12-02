#!/usr/bin/python

"""Test of page tab output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Popovers"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Right Arrow to the Page Setup page tab",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab'",
     "     VISIBLE:  'Page Setup page tab', cursor=1",
     "SPEECH OUTPUT: 'Page Setup page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Page Setup page tab Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab'",
     "     VISIBLE:  'Page Setup page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list.'",
     "SPEECH OUTPUT: 'Page Setup page tab.'",
     "SPEECH OUTPUT: '2 of [0-9]'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
