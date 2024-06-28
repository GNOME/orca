#!/usr/bin/python

"""Test of push button output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(KeyComboAction("p"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift+Tab to button",
    ["BRAILLE LINE:  'Firefox application Print dialog Print push button'",
     "     VISIBLE:  'Print push button', cursor=1",
     "SPEECH OUTPUT: 'Print push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Print dialog Print push button'",
     "     VISIBLE:  'Print push button', cursor=1",
     "SPEECH OUTPUT: 'Print push button.'",
     "SPEECH OUTPUT: 'Alt+P'"]))

sequence.append(TypeAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
