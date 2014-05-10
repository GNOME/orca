#!/usr/bin/python

"""Test dynamic header support."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Enable cell reading",
    ["BRAILLE LINE:  'Speak cell'",
     "     VISIBLE:  'Speak cell', cursor=0",
     "SPEECH OUTPUT: 'Speak cell' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow to cell A2",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1 Apples B1 Pears C1  D1  E1  F1  G1  H1  I1  J1  K1  L1'",
     "     VISIBLE:  ' A1 Apples B1 Pears C1  D1  E1  ', cursor=1",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Good in Pies A2'",
     "     VISIBLE:  'Good in Pies A2', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies A2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right Arrow to cell B2",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Yes B2'",
     "     VISIBLE:  'Yes B2', cursor=1",
     "SPEECH OUTPUT: 'Yes B2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow to cell B3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Yes B3'",
     "     VISIBLE:  'Yes B3', cursor=1",
     "SPEECH OUTPUT: 'Yes B3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right Arrow to cell C3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'Yes C3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Basic where am I with no dynamic headers set",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'table cell column 3 row 3 Yes'"]))

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("r"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Set dynamic column headers",
    ["BRAILLE LINE:  'Dynamic column header set for row 1'",
     "     VISIBLE:  'Dynamic column header set for ro', cursor=0",
     "SPEECH OUTPUT: 'Dynamic column header set for row 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("c"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Set dynamic row headers",
    ["KNOWN ISSUE: Why do we update braille here, but not for column headers",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1'",
     "     VISIBLE:  ' A1', cursor=1",
     "BRAILLE LINE:  'Dynamic row header set for column A'",
     "     VISIBLE:  'Dynamic row header set for colum', cursor=0",
     "SPEECH OUTPUT: 'Dynamic row header set for column A' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow to cell A2",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1'",
     "     VISIBLE:  ' A1', cursor=1",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Good in Pies A2'",
     "     VISIBLE:  'Good in Pies A2', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies A2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "10. Right Arrow to cell B2",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Good in Pies Apples Yes B2'",
     "     VISIBLE:  'Yes B2', cursor=1",
     "SPEECH OUTPUT: 'Apples Yes B2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down Arrow to cell B3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Juiceable Apples Yes B3'",
     "     VISIBLE:  'Yes B3', cursor=1",
     "SPEECH OUTPUT: 'Juiceable Yes B3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "12. Right Arrow to cell C3",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Juiceable Pears Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'Pears Yes C3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "13. Basic where am I with dynamic headers set",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Juiceable Pears Yes C3'",
     "     VISIBLE:  'Yes C3', cursor=1",
     "SPEECH OUTPUT: 'table cell column 3'",
     "SPEECH OUTPUT: 'Pears'",
     "SPEECH OUTPUT: 'row 3'",
     "SPEECH OUTPUT: 'Juiceable Yes'"]))

sequence.append(KeyComboAction("<Control>w"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
