#!/usr/bin/python

"""Test of presentation when typing in a cell."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("hi"))
sequence.append(utils.AssertPresentationAction(
    "1. Type 'hi' - keyecho is off",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Cell A1 panel Paragraph 0 hi $l'",
     "     VISIBLE:  'Paragraph 0 hi $l', cursor=15",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Cell A1 panel Paragraph 0 hi $l'",
     "     VISIBLE:  'Paragraph 0 hi $l', cursor=15",
     "SPEECH OUTPUT: 'Cell A1 panel'",
     "SPEECH OUTPUT: 'Paragraph 0 hi'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. Press Return",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Sheet Sheet1 table  A2'",
     "     VISIBLE:  ' A2', cursor=1",
     "SPEECH OUTPUT: 'Sheet Sheet1.'",
     "SPEECH OUTPUT: 'table with 1048576 rows 1024 columns'",
     "SPEECH OUTPUT: 'blank A2.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
