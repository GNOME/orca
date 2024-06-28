#!/usr/bin/python

"""Test of status bar output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Status bar Where Am I",
    ["BRAILLE LINE:  'Application Window'",
     "     VISIBLE:  'Application Window', cursor=0",
     "BRAILLE LINE:  'gtk-demo application Application Window frame Open push button'",
     "     VISIBLE:  'Open push button', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Application Window frame Open push button'",
     "     VISIBLE:  'Open push button', cursor=1",
     "SPEECH OUTPUT: 'Application Window'",
     "SPEECH OUTPUT: 'Cursor at row 0 column 0 - 0 chars in document'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
