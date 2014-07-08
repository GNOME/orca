#!/usr/bin/python

"""Test of labelled combo box output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Printing"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Combo box",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab Layout panel Only print: All sheets combo box'",
     "     VISIBLE:  'Only print: All sheets combo box', cursor=13",
     "SPEECH OUTPUT: 'Only print: All sheets combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab Layout panel Only print: All sheets combo box'",
     "     VISIBLE:  'Only print: All sheets combo box', cursor=13",
     "SPEECH OUTPUT: 'Only print:'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'All sheets'",
     "SPEECH OUTPUT: '1 of 3.'",
     "SPEECH OUTPUT: 'Alt+O'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Change selection",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab Layout panel  combo boxOnly print: Even sheets Even sheets'",
     "     VISIBLE:  'Even sheets', cursor=1",
     "SPEECH OUTPUT: 'Even sheets'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Where Am I",
    ["KNOWN ISSUE: We're a bit chatty here and the space is off with the combo box",
     "BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab Layout panel  combo boxOnly print: Even sheets Even sheets'",
     "     VISIBLE:  'Even sheets', cursor=1",
     "SPEECH OUTPUT: 'Print %'",
     "SPEECH OUTPUT: 'Page Setup'",
     "SPEECH OUTPUT: 'page tab'",
     "SPEECH OUTPUT: 'Layout'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: 'Even sheets'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'Even sheets'",
     "SPEECH OUTPUT: '2 of 3'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
