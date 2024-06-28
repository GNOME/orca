#!/usr/bin/python

"""Test of cell and row reading in Writer tables."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Up"))
sequence.append(PauseAction(5000))

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
    "2. Down Arrow",
    ["BRAILLE LINE:  'Mon $l'",
     "     VISIBLE:  'Mon $l', cursor=4",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank B2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["BRAILLE LINE:  '4 $l'",
     "     VISIBLE:  '4 $l', cursor=2",
     "SPEECH OUTPUT: '4 B3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Enable row reading",
    ["BRAILLE LINE:  'Speak row'",
     "     VISIBLE:  'Speak row', cursor=0",
     "SPEECH OUTPUT: 'Speak row' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow",
    ["BRAILLE LINE:  '4 $l'",
     "     VISIBLE:  '4 $l', cursor=2",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'A2 B2 C2 D2 E2'",
     "SPEECH OUTPUT: '1 F2 2 G2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up Arrow",
    ["BRAILLE LINE:  'Mon $l'",
     "     VISIBLE:  'Mon $l', cursor=4",
     "SPEECH OUTPUT: 'Sun A1 Mon B1 Tue C1 Wed D1 Thu E1 Fri F1 Sat G1.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
