#!/usr/bin/python

"""Test of cell and row reading in Writer tables."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

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
    "2. Down Arrow to the Mon table column header with cell reading enabled",
    ["BRAILLE LINE:  'This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "BRAILLE LINE:  'Mon $l'",
     "     VISIBLE:  'Mon $l', cursor=4",
     "SPEECH OUTPUT: 'Calendar-1 table with 7 rows 7 columns'",
     "SPEECH OUTPUT: 'Mon'"]))

sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Enable row reading",
    ["BRAILLE LINE:  'Speak row'",
     "     VISIBLE:  'Speak row', cursor=0",
     "SPEECH OUTPUT: 'Speak row' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow to the Mon table column header with row reading enabled",
    ["BRAILLE LINE:  'This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "BRAILLE LINE:  'Mon $l'",
     "     VISIBLE:  'Mon $l', cursor=4",
     "SPEECH OUTPUT: 'Calendar-1 table with 7 rows 7 columns'",
     "SPEECH OUTPUT: 'Sun Mon Tue Wed Thu Fri Sat'"]))

sequence.append(KeyComboAction("<Control>w"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
