#!/usr/bin/python

"""Test to verify SayAll works in Writer."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 3"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 4"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Return to top of document",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document Line 1 $l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "2. Say all on document",
    ["SPEECH OUTPUT: 'Line 1'",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'Line 3'",
     "SPEECH OUTPUT: 'Line 4'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
