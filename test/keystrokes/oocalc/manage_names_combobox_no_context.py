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
    ["BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar A1 $l combo box'",
     "     VISIBLE:  'A1 $l combo box', cursor=3",
     "SPEECH OUTPUT: 'Formula Tool Bar tool bar'",
     "SPEECH OUTPUT: 'Name Box editable combo box.'",
     "SPEECH OUTPUT: 'A1 selected'"]))

sequence.append(KeyComboAction("<Control>a"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C3"))
sequence.append(utils.AssertPresentationAction(
    "2. Type 'C3' - keyecho is disabled",
    ["BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Name Box C $l'",
     "     VISIBLE:  'C $l', cursor=2",
     "BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar Name Box C3 $l'",
     "     VISIBLE:  'C3 $l', cursor=3"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Press Return to jump to C3",
    ["BRAILLE LINE:  'Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Untitled1 - LibreOffice Spreadsheets Sheet Sheet1 table  C3'",
     "     VISIBLE:  ' C3', cursor=1",
     "SPEECH OUTPUT: 'blank C3.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
