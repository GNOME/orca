#!/usr/bin/python

"""Test of window title output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Window Where Am I",
    ["BRAILLE LINE:  'GTK+ Code Demos'",
     "     VISIBLE:  'GTK+ Code Demos', cursor=0",
     "SPEECH OUTPUT: 'GTK+ Code Demos'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
