#!/usr/bin/python

"""Test presentation of caret navigation by line."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Return to top of document",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document Line 1 $l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Arrow down to 'Line 2'",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Arrow down over the empty line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Arrow up to 'Line 2'",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Arrow up to 'Line 1'",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document Line 1 $l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
