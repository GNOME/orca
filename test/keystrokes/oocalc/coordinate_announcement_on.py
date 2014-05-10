#!/usr/bin/python

"""Test presentation when coordinate announcement is on"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(2000))
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
    "2. Down to A2 - don't speak cell coordinates",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1 Apples B1 Pears C1  D1  E1  F1  G1  H1  I1  J1  K1  L1'",
     "     VISIBLE:  ' A1 Apples B1 Pears C1  D1  E1  ', cursor=1",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Good in Pies A2'",
     "     VISIBLE:  'Good in Pies A2', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies A2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right to B2 - don't speak cell coordinates",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table Yes B2'",
     "     VISIBLE:  'Yes B2', cursor=1",
     "SPEECH OUTPUT: 'Yes B2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "4. Control+Home to A1 - don't speak cell coordinates",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame fruit.ods - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1'",
     "     VISIBLE:  ' A1', cursor=1",
     "SPEECH OUTPUT: 'blank A1'"]))

sequence.append(KeyComboAction("<Control>w"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
