#!/usr/bin/python

"""Test of Dojo toolbar presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow",
    ["BRAILLE LINE:  'Toolbar from markup h2'",
     "     VISIBLE:  'Toolbar from markup h2', cursor=1",
     "SPEECH OUTPUT: 'Toolbar from markup'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["BRAILLE LINE:  'input before toolbar1 $l'",
     "     VISIBLE:  'input before toolbar1 $l', cursor=1",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'input before toolbar1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["BRAILLE LINE:  'Buttons: '",
     "     VISIBLE:  'Buttons: ', cursor=1",
     "SPEECH OUTPUT: 'Buttons: '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow",
    ["KNOWN ISSUE: These results are not correct here and in the following assertions",
     "BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right Arrow on toolbar",
    ["BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Right Arrow on toolbar",
    ["BRAILLE LINE:  'Copy'",
     "     VISIBLE:  'Copy', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Left Arrow on toolbar",
    ["BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "8. End to last widget on toolbar",
    ["BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow",
    ["BRAILLE LINE:  'Copy'",
     "     VISIBLE:  'Copy', cursor=1",
     "SPEECH OUTPUT: 'Copy'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down Arrow",
    ["BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down Arrow",
    ["BRAILLE LINE:  ' Toggles: '",
     "     VISIBLE:  ' Toggles: ', cursor=1",
     "SPEECH OUTPUT: ' Toggles: '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down Arrow",
    ["BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "13. Right Arrow on toolbar",
    ["BRAILLE LINE:  'push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
