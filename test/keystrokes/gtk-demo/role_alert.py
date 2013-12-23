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
    "Initial dialog",
    ["BRAILLE LINE:  'gtk-demo application Dialogs frame'",
     "     VISIBLE:  'Dialogs frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Dialogs frame Dialogs panel Message Dialog push button'",
     "     VISIBLE:  'Message Dialog push button', cursor=1",
     "SPEECH OUTPUT: 'Dialogs frame'",
     "SPEECH OUTPUT: 'Dialogs panel'",
     "SPEECH OUTPUT: 'Message Dialog push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "Information alert",
    ["BRAILLE LINE:  'gtk-demo application Information alert'",
     "     VISIBLE:  'Information alert', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Information alert OK push button'",
     "     VISIBLE:  'OK push button', cursor=1",
     "SPEECH OUTPUT: 'Information This message box has been popped up the following",
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
    "Entry 1",
    ["BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog'",
     "     VISIBLE:  'Interactive Dialog dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog Entry 1 Testing $l'",
     "     VISIBLE:  'Entry 1 Testing $l', cursor=16",
     "SPEECH OUTPUT: 'Interactive Dialog'",
     "SPEECH OUTPUT: 'Entry 1 text Testing selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Entry 2",
    ["BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog Entry 2 Again $l'",
     "     VISIBLE:  'Entry 2 Again $l', cursor=14",
     "BRAILLE LINE:  'gtk-demo application Interactive Dialog dialog Entry 2 Again $l'",
     "     VISIBLE:  'Entry 2 Again $l', cursor=14",
     "SPEECH OUTPUT: 'Entry 2 text Again selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Title bar",
    ["BRAILLE LINE:  'Interactive Dialog'",
     "     VISIBLE:  'Interactive Dialog', cursor=0",
     "SPEECH OUTPUT: 'Interactive Dialog'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
