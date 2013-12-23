#!/usr/bin/python

"""Test of status bar output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Status bar Where Am I",
    ["BRAILLE LINE:  'Application Class'",
     "     VISIBLE:  'Application Class', cursor=0",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Cursor at row 0 column 0 - 0 chars in document'",
     "     VISIBLE:  'Cursor at row 0 column 0 - 0 cha', cursor=0",
     "SPEECH OUTPUT: 'Application Class'",
     "SPEECH OUTPUT: 'Cursor at row 0 column 0 - 0 chars in document'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
