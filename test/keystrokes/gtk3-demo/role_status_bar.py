#!/usr/bin/python

"""Test of status bar output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("1"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Status bar Where Am I",
    ["KNOWN ISSUE: We might not want the 'frame' visible",
     "BRAILLE LINE:  'Application Class'",
     "     VISIBLE:  'Application Class', cursor=0",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame  $l'",
     "     VISIBLE:  'frame  $l', cursor=7",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame  $l'",
     "     VISIBLE:  'frame  $l', cursor=7",
     "SPEECH OUTPUT: 'Application Class'",
     "SPEECH OUTPUT: 'Cursor at row 0 column 0 - 0 chars in document'",
     "SPEECH OUTPUT: 'Information'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
