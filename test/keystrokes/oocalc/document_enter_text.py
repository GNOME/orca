#!/usr/bin/python

"""Test of presentation when typing in a cell."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("h"))
sequence.append(utils.AssertPresentationAction(
    "1. Type 'h' - keyecho is off",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Untitled 1 - LibreOffice Spreadsheets Cell A1 panel h $l'",
     "     VISIBLE:  'h $l', cursor=2",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Input line Input line $l h $l'",
     "     VISIBLE:  'h $l', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("i"))
sequence.append(utils.AssertPresentationAction(
    "2. Type 'i' - keyecho is off",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Untitled 1 - LibreOffice Spreadsheets Cell A1 panel hi $l'",
     "     VISIBLE:  'hi $l', cursor=3"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "3. Press Return",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Untitled 1 - LibreOffice Spreadsheets Sheet Sheet1 table  A2'",
     "     VISIBLE:  'table  A2', cursor=7",
     "SPEECH OUTPUT: 'blank A2.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
