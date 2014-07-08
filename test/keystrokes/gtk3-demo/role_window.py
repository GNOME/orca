#!/usr/bin/python

"""Test of window title output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Window Where Am I",
    ["BRAILLE LINE:  'Application Class'",
     "     VISIBLE:  'Application Class', cursor=0",
     "SPEECH OUTPUT: 'Application Class'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
