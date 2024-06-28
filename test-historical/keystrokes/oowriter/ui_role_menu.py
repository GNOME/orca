#!/usr/bin/python

"""Test to verify result of entering and escaping out of a submenu."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Alt>f"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("w"))
sequence.append(utils.AssertPresentationAction(
    "1. Open the Wizards submenu",
    ["BRAILLE LINE:  'soffice application Wizards menu'",
     "     VISIBLE:  'soffice application Wizards menu', cursor=21",
     "BRAILLE LINE:  'soffice application File menu Letter...'",
     "     VISIBLE:  'Letter...', cursor=1",
     "SPEECH OUTPUT: 'Wizards menu.'",
     "SPEECH OUTPUT: 'Letter...'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "2. Exit the Wizards submenu, which now returns you to the document",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame'",
     "     VISIBLE:  'Untitled 1 - LibreOffice Writer ', cursor=1",
     "SPEECH OUTPUT: 'Untitled 1 - LibreOffice Writer frame'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
