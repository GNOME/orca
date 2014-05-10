#!/usr/bin/python

"""Test of messages associated with dynamic headers."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("r"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Set column headers",
    ["BRAILLE LINE:  'Dynamic column header set for row 1'",
     "     VISIBLE:  'Dynamic column header set for ro', cursor=0",
     "SPEECH OUTPUT: 'Dynamic column header set for row 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("r"))
sequence.append(KeyComboAction("r"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Clear column headers",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1  B1  C1  D1  E1  F1  G1  H1  I1  J1  K1  L1  M1'",
     "     VISIBLE:  ' A1  B1  C1  D1  E1  F1  G1  H1 ', cursor=1",
     "BRAILLE LINE:  'Dynamic column header set for row 1'",
     "     VISIBLE:  'Dynamic column header set for ro', cursor=0",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1  B1  C1  D1  E1  F1  G1  H1  I1  J1  K1  L1  M1'",
     "     VISIBLE:  ' A1  B1  C1  D1  E1  F1  G1  H1 ', cursor=1",
     "BRAILLE LINE:  'Dynamic column header cleared.'",
     "     VISIBLE:  'Dynamic column header cleared.', cursor=0",
     "SPEECH OUTPUT: 'Dynamic column header set for row 1' voice=system",
     "SPEECH OUTPUT: 'Dynamic column header cleared.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("c"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Set row headers",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1  B1  C1  D1  E1  F1  G1  H1  I1  J1  K1  L1  M1'",
     "     VISIBLE:  ' A1  B1  C1  D1  E1  F1  G1  H1 ', cursor=1",
     "BRAILLE LINE:  'Dynamic row header set for column A'",
     "     VISIBLE:  'Dynamic row header set for colum', cursor=0",
     "SPEECH OUTPUT: 'Dynamic row header set for column A' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("c"))
sequence.append(KeyComboAction("c"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Clear row headers",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1  B1  C1  D1  E1  F1  G1  H1  I1  J1  K1  L1  M1'",
     "     VISIBLE:  ' A1  B1  C1  D1  E1  F1  G1  H1 ', cursor=1",
     "BRAILLE LINE:  'Dynamic row header set for column A'",
     "     VISIBLE:  'Dynamic row header set for colum', cursor=0",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1  B1  C1  D1  E1  F1  G1  H1  I1  J1  K1  L1  M1'",
     "     VISIBLE:  ' A1  B1  C1  D1  E1  F1  G1  H1 ', cursor=1",
     "BRAILLE LINE:  'Dynamic row header cleared.'",
     "     VISIBLE:  'Dynamic row header cleared.', cursor=0",
     "SPEECH OUTPUT: 'Dynamic row header set for column A' voice=system",
     "SPEECH OUTPUT: 'Dynamic row header cleared.' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
