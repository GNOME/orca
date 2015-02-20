#!/usr/bin/python

"""Test of labelled combo box output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Printing"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Right"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(utils.AssertPresentationAction(
    "1. Combo box",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab Layout panel Only print: All sheets combo box'",
     "     VISIBLE:  'Only print: All sheets combo box', cursor=13",
     "SPEECH OUTPUT: 'Layout panel'",
     "SPEECH OUTPUT: 'Only print: All sheets combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab Layout panel Only print: All sheets combo box'",
     "     VISIBLE:  'Only print: All sheets combo box', cursor=13",
     "SPEECH OUTPUT: 'Only print: combo box All sheets 1 of 3.'",
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
    ["KNOWN ISSUE: The combo box role is missing and spacing is wrong in braille",
     "BRAILLE LINE:  'gtk3-demo application Print dialog Page Setup page tab Layout panel  combo boxOnly print: Even sheets Even sheets'",
     "     VISIBLE:  'Even sheets', cursor=1",
     "SPEECH OUTPUT: 'Print'",
     "SPEECH OUTPUT: 'Page Setup page tab'",
     "SPEECH OUTPUT: 'Layout panel'",
     "SPEECH OUTPUT: 'Even sheets 2 of 3'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
