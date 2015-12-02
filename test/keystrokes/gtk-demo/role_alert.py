#!/usr/bin/python

"""Test of presentation of dialogs and alerts."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Dialog and Message Boxes"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "1. Information alert",
    ["BRAILLE LINE:  'gtk-demo application Information alert'",
     "     VISIBLE:  'Information alert', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Information alert OK push button'",
     "     VISIBLE:  'OK push button', cursor=1",
     "SPEECH OUTPUT: 'Information alert.'",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: 1'",
     "SPEECH OUTPUT: 'OK push button'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Down"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("Testing"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("Again"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>i"))
sequence.append(utils.AssertPresentationAction(
    "2. Entry 1",
    ["BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog'",
     "     VISIBLE:  'Interactive Dialog dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog Entry 1 Testing $l'",
     "     VISIBLE:  'Entry 1 Testing $l', cursor=16",
     "SPEECH OUTPUT: 'Interactive Dialog'",
     "SPEECH OUTPUT: 'Entry 1 text.'",
     "SPEECH OUTPUT: 'Testing selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Entry 2",
    ["BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog Entry 2 Again $l'",
     "     VISIBLE:  'Entry 2 Again $l', cursor=14",
     "BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog Entry 2 Again $l'",
     "     VISIBLE:  'Entry 2 Again $l', cursor=14",
     "SPEECH OUTPUT: 'Entry 2 text.'",
     "SPEECH OUTPUT: 'Again selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Title bar",
    ["BRAILLE LINE:  'Interactive Dialog'",
     "     VISIBLE:  'Interactive Dialog', cursor=0",
     "SPEECH OUTPUT: 'Interactive Dialog'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
