#!/usr/bin/python

"""Test dynamic header support."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow to cell A2",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Good in Pies A2'",
     "     VISIBLE:  'Good in Pies A2', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies A2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right Arrow to cell B2",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Yes B2'",
     "     VISIBLE:  'Yes B2', cursor=1",
     "SPEECH OUTPUT: 'Yes B2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow to cell B3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Yes B3'",
     "     VISIBLE:  'Yes B3', cursor=1",
     "SPEECH OUTPUT: 'Yes B3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Right Arrow to cell C3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'Yes C3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "5. Basic where am I with no dynamic headers set",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'column 3.'",
     "SPEECH OUTPUT: 'row 3.'",
     "SPEECH OUTPUT: 'Yes.'"]))

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("r"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Set dynamic column headers",
    ["BRAILLE LINE:  'Dynamic column header set for row 1'",
     "     VISIBLE:  'Dynamic column header set for ro', cursor=0",
     "SPEECH OUTPUT: 'Dynamic column header set for row 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("c"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Set dynamic row headers",
    ["KNOWN ISSUE - We don't want to show the sheet here",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table  A1'",
     "     VISIBLE:  'Sheet Sheet1 table  A1', cursor=20",
     "BRAILLE LINE:  'Dynamic row header set for column A'",
     "     VISIBLE:  'Dynamic row header set for colum', cursor=0",
     "SPEECH OUTPUT: 'Dynamic row header set for column A' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down Arrow to cell A2",
    ["KNOWN ISSUE - We don't want to show the sheet here",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table  A1'",
     "     VISIBLE:  'Sheet Sheet1 table  A1', cursor=20",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Good in Pies A2'",
     "     VISIBLE:  'Good in Pies A2', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies A2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "9. Right Arrow to cell B2",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Good in Pies Apples Yes B2'",
     "     VISIBLE:  'Yes B2', cursor=1",
     "SPEECH OUTPUT: 'Apples Yes B2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down Arrow to cell B3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Juiceable Apples Yes B3'",
     "     VISIBLE:  'Yes B3', cursor=1",
     "SPEECH OUTPUT: 'Juiceable Yes B3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Right Arrow to cell C3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Juiceable Pears Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'Pears Yes C3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "12. Basic where am I with dynamic headers set",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Juiceable Pears Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'column 3.'",
     "SPEECH OUTPUT: 'Pears.'",
     "SPEECH OUTPUT: 'row 3.'",
     "SPEECH OUTPUT: 'Juiceable.'",
     "SPEECH OUTPUT: 'Yes.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
