#!/usr/bin/python

"""Test presentation of character attributes."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Attributes of cell A2",
    ["SPEECH OUTPUT: 'size: 16' voice=system",
     "SPEECH OUTPUT: 'family name: Arial' voice=system",
     "SPEECH OUTPUT: 'bold' voice=system",
     "SPEECH OUTPUT: 'style: italic' voice=system"]))

sequence.append(KeyComboAction("Right"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Attributes of cell B2",
    ["SPEECH OUTPUT: 'size: 10' voice=system",
     "SPEECH OUTPUT: 'family name: Arial' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
