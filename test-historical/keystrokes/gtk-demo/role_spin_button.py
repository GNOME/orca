#!/usr/bin/python

"""Test of spin button output"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Printing"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Alt>s"))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>s"))
sequence.append(utils.AssertPresentationAction(
    "1. Give focus to spin button",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies: 1 $l'",
     "     VISIBLE:  'Copies: 1 $l', cursor=10",
     "SPEECH OUTPUT: 'Copies: 1 selected spin button.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies: 1 $l'",
     "     VISIBLE:  'Copies: 1 $l', cursor=10",
     "SPEECH OUTPUT: 'Copies: spin button 1 selected.'",
     "SPEECH OUTPUT: 'Alt+S'"]))

sequence.append(TypeAction("15"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Increment value",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies: 16 $l'",
     "     VISIBLE:  'Copies: 16 $l', cursor=9",
     "SPEECH OUTPUT: '16'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Decrement value",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies: 15 $l'",
     "     VISIBLE:  'Copies: 15 $l', cursor=9",
     "SPEECH OUTPUT: '15'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Caret navigation",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab Copies: 15 $l'",
     "     VISIBLE:  'Copies: 15 $l', cursor=10",
     "SPEECH OUTPUT: '5'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
