#!/usr/bin/python

"""Test of table output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Table Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Shopping list frame table Number column header 3 bottles of coke'",
     "     VISIBLE:  '3 bottles of coke', cursor=1",
     "SPEECH OUTPUT: 'table.'",
     "SPEECH OUTPUT: 'Number.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: '3.'",
     "SPEECH OUTPUT: 'column 1 of 3'",
     "SPEECH OUTPUT: 'row 1 of 5.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Next row",
    ["BRAILLE LINE:  'gtk-demo application Shopping list frame table Number column header 5 packages of noodles'",
     "     VISIBLE:  '5 packages of noodles', cursor=1",
     "SPEECH OUTPUT: '5 packages of noodles.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Table Where Am I (again)",
    ["BRAILLE LINE:  'gtk-demo application Shopping list frame table Number column header 5 packages of noodles'",
     "     VISIBLE:  '5 packages of noodles', cursor=1",
     "SPEECH OUTPUT: 'table.'",
     "SPEECH OUTPUT: 'Number.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: '5.'",
     "SPEECH OUTPUT: 'column 1 of 3'",
     "SPEECH OUTPUT: 'row 2 of 5.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Turn row reading off",
    ["BRAILLE LINE:  'Speak cell'",
     "     VISIBLE:  'Speak cell', cursor=0",
     "SPEECH OUTPUT: 'Speak cell'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Table Right to the Product column in the packages of noodles row",
    ["BRAILLE LINE:  'gtk-demo application Shopping list frame table Number column header 5 packages of noodles'",
     "     VISIBLE:  '5 packages of noodles', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Shopping list frame table Product column header packages of noodles table cell'",
     "     VISIBLE:  'packages of noodles table cell', cursor=1",
     "SPEECH OUTPUT: 'Product column header packages of noodles.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Table up to bottles of coke",
    ["BRAILLE LINE:  'gtk-demo application Shopping list frame table Product column header bottles of coke table cell'",
     "     VISIBLE:  'bottles of coke table cell', cursor=1",
     "SPEECH OUTPUT: 'bottles of coke.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
