#!/usr/bin/python

"""Test to verify result of entering and escaping out of a submenu."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Alt>f"))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("w"))
sequence.append(utils.AssertPresentationAction(
    "1. Open the Wizards submenu",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame (1 dialog) Untitled 1 - LibreOffice Writer root pane Wizards menu'",
     "     VISIBLE:  'Wizards menu', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame (1 dialog) Untitled 1 - LibreOffice Writer root pane File menu Letter...'",
     "     VISIBLE:  'Letter...', cursor=1",
     "SPEECH OUTPUT: 'Wizards menu'",
     "SPEECH OUTPUT: 'Letter...'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "2. Exit the Wizards submenu",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame (1 dialog) Untitled 1 - LibreOffice Writer root pane Wizards menu'",
     "     VISIBLE:  'Wizards menu', cursor=1",
     "SPEECH OUTPUT: 'Wizards menu'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
