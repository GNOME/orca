#!/usr/bin/python

"""Test presentation of caret navigation by line in list with bullets."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Shift>F12"))
sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 3"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down to next bulleted line",
    ["BRAILLE LINE:  '• Line 2 $l'",
     "     VISIBLE:  '• Line 2 $l', cursor=3",
     "SPEECH OUTPUT: '• Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down to next bulleted line",
    ["BRAILLE LINE:  '• Line 3 $l'",
     "     VISIBLE:  '• Line 3 $l', cursor=3",
     "SPEECH OUTPUT: '• Line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up to previous bulleted line",
    ["BRAILLE LINE:  '• Line 2 $l'",
     "     VISIBLE:  '• Line 2 $l', cursor=3",
     "SPEECH OUTPUT: '• Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up to previous bulleted line",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document • Line 1 $l'",
     "     VISIBLE:  '• Line 1 $l', cursor=3",
     "SPEECH OUTPUT: '• Line 1'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
