#!/usr/bin/python

"""Test presentation of the Manage Names combobox"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>t"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift+Ctrl+T",
    ["KNOWN ISSUE: This is too chatty",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar A1 $l'",
     "     VISIBLE:  'A1 $l', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar A1 $l combo box'",
     "     VISIBLE:  'A1 $l combo box', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar  combo boxA1 $l Manage Names... list item'",
     "     VISIBLE:  'Manage Names... list item', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar A1 $l'",
     "     VISIBLE:  'A1 $l', cursor=1",
     "SPEECH OUTPUT: 'A1 combo box'",
     "SPEECH OUTPUT: 'text A1'",
     "SPEECH OUTPUT: 'A1 combo box'",
     "SPEECH OUTPUT: 'Manage Names...'",
     "SPEECH OUTPUT: 'text A1'"]))

sequence.append(KeyComboAction("<Control>a"))
sequence.append(KeyComboAction("BackSpace"))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C3"))
sequence.append(utils.AssertPresentationAction(
    "2. Type 'C3' - keyecho is disabled",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar C $l'",
     "     VISIBLE:  'C $l', cursor=2",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar C $l'",
     "     VISIBLE:  'C $l', cursor=2",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar C3 $l'",
     "     VISIBLE:  'C3 $l', cursor=3",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Formula Tool Bar tool bar C3 $l'",
     "     VISIBLE:  'C3 $l', cursor=3"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Press Return to jump to C3",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A3  B3  C3  D3  E3  F3  G3  H3  I3  J3  K3  L3  M3'",
     "     VISIBLE:  ' C3  D3  E3  F3  G3  H3  I3  J3 ', cursor=1",
     "SPEECH OUTPUT: 'Sheet Sheet1 table with 1048576 rows 1024 columns'",
     "SPEECH OUTPUT: 'blank C3'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
