#!/usr/bin/python

"""Test of presentation when typing in a cell."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("h"))
sequence.append(utils.AssertPresentationAction(
    "1. Type 'h' - keyecho is off",
    ["BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Cell A1 panel Paragraph 0 h $l'",
     "     VISIBLE:  'Paragraph 0 h $l', cursor=14",
     "SPEECH OUTPUT: 'Cell A1 panel'",
     "SPEECH OUTPUT: 'Paragraph 0 h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("i"))
sequence.append(utils.AssertPresentationAction(
    "2. Type 'i' - keyecho is off",
    ["BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Cell A1 panel Paragraph 0 hi $l'",
     "     VISIBLE:  'Paragraph 0 hi $l', cursor=15",
     "BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Cell A1 panel Paragraph 0 hi $l'",
     "     VISIBLE:  'Paragraph 0 hi $l', cursor=15"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "3. Press Return",
    ["BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Sheet Sheet1 table  A2'",
     "     VISIBLE:  ' A2', cursor=1",
     "SPEECH OUTPUT: 'blank A2.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
