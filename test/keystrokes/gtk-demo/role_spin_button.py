#!/usr/bin/python

"""Test of spin button output"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Printing"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>s"))
sequence.append(utils.AssertPresentationAction(
    "Give focus to spin button",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 1 $l'",
     "     VISIBLE:  'Copies: 1 $l', cursor=10",
     "BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 1 $l'",
     "     VISIBLE:  'Copies: 1 $l', cursor=10",
     "SPEECH OUTPUT: 'Copies'",
     "SPEECH OUTPUT: 'Copies: 1 selected spin button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 1 $l'",
     "     VISIBLE:  'Copies: 1 $l', cursor=10",
     "SPEECH OUTPUT: 'Copies:'",
     "SPEECH OUTPUT: 'spin button'",
     "SPEECH OUTPUT: '1'",
     "SPEECH OUTPUT: 'selected.'",
     "SPEECH OUTPUT: 'Alt+S'"]))

sequence.append(TypeAction("15"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Increment value",
    ["KNOWN ISSUE: We are double-presenting this",
     "BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 16 $l'",
     "     VISIBLE:  'Copies: 16 $l', cursor=9",
     "BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 16 $l'",
     "     VISIBLE:  'Copies: 16 $l', cursor=9",
     "BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 16 $l'",
     "     VISIBLE:  'Copies: 16 $l', cursor=9",
     "SPEECH OUTPUT: '16'",
     "SPEECH OUTPUT: '16'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Decrement value",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 15 $l'",
     "     VISIBLE:  'Copies: 15 $l', cursor=9",
     "BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 15 $l'",
     "     VISIBLE:  'Copies: 15 $l', cursor=9",
     "SPEECH OUTPUT: '15'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Caret navigation",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies filler Copies: 15 $l'",
     "     VISIBLE:  'Copies: 15 $l', cursor=10",
     "SPEECH OUTPUT: '5'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
