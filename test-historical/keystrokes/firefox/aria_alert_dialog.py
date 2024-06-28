#!/usr/bin/python

"""Test of UIUC button presentation using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(TypeAction("12"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Open Alert Box",
    ["BRAILLE LINE:  'dialog'",
     "     VISIBLE:  'dialog', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Alert Box You must choose a number between 1 and 10!'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down to message",
    ["BRAILLE LINE:  'dialog'",
     "     VISIBLE:  'dialog', cursor=1",
     "BRAILLE LINE:  'You must choose a number'",
     "     VISIBLE:  'You must choose a number', cursor=1",
     "SPEECH OUTPUT: 'You must choose a number'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down arrow to read next line of message",
    ["BRAILLE LINE:  'between 1 and 10!'",
     "     VISIBLE:  'between 1 and 10!', cursor=1",
     "SPEECH OUTPUT: 'between 1 and 10!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down arrow to read next line of message",
    ["BRAILLE LINE:  'Close push button'",
     "     VISIBLE:  'Close push button', cursor=1",
     "SPEECH OUTPUT: 'Close push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "5. Close Alert",
    ["BRAILLE LINE:  'Guess a number between 1 and 10 12 $l invalid'",
     "     VISIBLE:  '12 $l invalid', cursor=3",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Guess a number between 1 and 10 entry 12 selected.'",
     "SPEECH OUTPUT: 'invalid entry'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
