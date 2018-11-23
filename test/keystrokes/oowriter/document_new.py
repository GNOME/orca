#!/usr/bin/python

"""Test to verify what is announced when you create a new document."""

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>N"))
sequence.append(PauseAction(5000))
sequence.append(utils.AssertPresentationAction(
    "New text document",
    ["BRAILLE LINE:  'soffice application Untitled 2 - LibreOffice Writer frame'",
     "     VISIBLE:  'Untitled 2 - LibreOffice Writer ', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 2 - LibreOffice Writer root pane Untitled 2 - LibreOffice Document  $l'",
     "     VISIBLE:  'Document  $l', cursor=10",
     "SPEECH OUTPUT: 'Untitled 2 - LibreOffice Writer frame'",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
