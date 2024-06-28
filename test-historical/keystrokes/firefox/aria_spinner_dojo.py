#!/usr/bin/python

"""Test of Dojo spinner presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to the first spinner",
    ["BRAILLE LINE:  'Spinbox #1: 900 $l'",
     "     VISIBLE:  'Spinbox #1: 900 $l', cursor=16",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'Spinbox #1: 900 selected spin button.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Decrement first spinner",
    ["BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=16",
     "SPEECH OUTPUT: '899'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Decrement first spinner",
    ["BRAILLE LINE:  'Spinbox #1: 898 $l'",
     "     VISIBLE:  'Spinbox #1: 898 $l', cursor=16",
     "SPEECH OUTPUT: '898'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Increment first spinner",
    ["BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=16",
     "SPEECH OUTPUT: '899'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "5. basic whereAmI",
    ["BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=16",
     "SPEECH OUTPUT: 'Spinbox #1: spin button 899.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
