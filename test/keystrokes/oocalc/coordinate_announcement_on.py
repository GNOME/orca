#!/usr/bin/python

"""Test presentation when coordinate announcement is on"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down to A2 - speak cell coordinates",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Good in Pies A2'",
     "     VISIBLE:  'Good in Pies A2', cursor=1",
     "SPEECH OUTPUT: 'Good in Pies A2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right to B2 - speak cell coordinates",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table Yes B2'",
     "     VISIBLE:  'Yes B2', cursor=1",
     "SPEECH OUTPUT: 'Yes B2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "4. Control+Home to A1 - speak cell coordinates",
    ["KNOWN ISSUE: We don't want to show the sheet.",
     "BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc root pane Sheet Sheet1 table  A1'",
     "     VISIBLE:  'Sheet Sheet1 table  A1', cursor=20",
     "SPEECH OUTPUT: 'blank A1.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
