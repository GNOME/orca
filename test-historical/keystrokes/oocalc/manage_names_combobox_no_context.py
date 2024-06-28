#!/usr/bin/python

"""Test presentation of the Manage Names combobox"""

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>t"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift+Ctrl+T",
    ["KNOWN ISSUE: We're speaking the name box twice",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Name Box A1 $l'",
     "     VISIBLE:  'Name Box A1 $l', cursor=12",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar A1 $l combo box'",
     "     VISIBLE:  'tool bar A1 $l combo box', cursor=12",
     "SPEECH OUTPUT: 'A1'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'Formula Tool Bar tool bar'",
     "SPEECH OUTPUT: 'Name Box Name Box editable combo box.'",
     "SPEECH OUTPUT: 'A1 selected'"]))

sequence.append(KeyComboAction("<Control>a"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C3"))
sequence.append(utils.AssertPresentationAction(
    "2. Type 'C3' - keyecho is disabled",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Name Box C $l'",
     "     VISIBLE:  'Name Box C $l', cursor=11",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Name Box C $l'",
     "     VISIBLE:  'Name Box C $l', cursor=11",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Name Box C3 $l'",
     "     VISIBLE:  'Name Box C3 $l', cursor=12",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Name Box C3 $l'",
     "     VISIBLE:  'Name Box C3 $l', cursor=12"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Press Return to jump to C3",
    ["KNOWN ISSUE: We don't want to show the table here",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Untitled 1 - LibreOffice Spreadsheets Sheet Sheet1 table'",
     "     VISIBLE:  'Sheet Sheet1 table', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc root pane Untitled 1 - LibreOffice Spreadsheets Sheet Sheet1 table  C3'",
     "     VISIBLE:  'table  C3', cursor=7",
     "SPEECH OUTPUT: 'Sheet Sheet1.'",
     "SPEECH OUTPUT: 'table with 1048576 rows 1024 columns'",
     "SPEECH OUTPUT: 'blank C3.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
