#!/usr/bin/python

"""Test of presentation when typing in a cell."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(2000))

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("hi"))
sequence.append(utils.AssertPresentationAction(
    "1. Type 'hi' - keyecho is off",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A1  B1  C1  D1  E1  F1  G1  H1  I1  J1  K1  L1  M1'",
     "     VISIBLE:  ' A1  B1  C1  D1  E1  F1  G1  H1 ', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Cell A1 h $l'",
     "     VISIBLE:  'h $l', cursor=2",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Cell A1 hi $l'",
     "     VISIBLE:  'hi $l', cursor=3",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Cell A1 hi $l'",
     "     VISIBLE:  'hi $l', cursor=3"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Press Return",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table hi A1'",
     "     VISIBLE:  'hi A1', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Calc frame Untitled 1 - LibreOffice Calc root pane Document view3 Sheet Sheet1 table  A2'",
     "     VISIBLE:  ' A2', cursor=1",
     "SPEECH OUTPUT: 'hi A1'",
     "SPEECH OUTPUT: 'blank A2'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
