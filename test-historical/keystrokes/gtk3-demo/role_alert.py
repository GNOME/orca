#!/usr/bin/python

"""Test of presentation of dialogs and alerts."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(PauseAction(1000))
sequence.append(TypeAction("Dialog and Message Boxes"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "1. Initial dialog",
    ["BRAILLE LINE:  'gtk3-demo application Dialogs and Message Boxes frame'",
     "     VISIBLE:  'Dialogs and Message Boxes frame', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Dialogs and Message Boxes frame Dialogs panel Message Dialog push button'",
     "     VISIBLE:  'Message Dialog push button', cursor=1",
     "SPEECH OUTPUT: 'Dialogs and Message Boxes frame'",
     "SPEECH OUTPUT: 'Dialogs panel.'",
     "SPEECH OUTPUT: 'Message Dialog push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "2. Information alert",
    ["BRAILLE LINE:  'gtk3-demo application Information alert'",
     "     VISIBLE:  'Information alert', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Information alert Cancel push button'",
     "     VISIBLE:  'Cancel push button', cursor=1",
     "SPEECH OUTPUT: 'Information alert.'",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: 1'",
     "SPEECH OUTPUT: 'Cancel push button'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Down"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("Testing"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("Again"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>i"))
sequence.append(utils.AssertPresentationAction(
    "3. Entry 1",
    ["BRAILLE LINE:  'gtk3-demo application Interactive Dialog dialog'",
     "     VISIBLE:  'Interactive Dialog dialog', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Interactive Dialog dialog Entry 1 Testing $l'",
     "     VISIBLE:  'Entry 1 Testing $l', cursor=16",
     "SPEECH OUTPUT: 'Interactive Dialog'",
     "SPEECH OUTPUT: 'Entry 1 text.'",
     "SPEECH OUTPUT: 'Testing selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Entry 2",
    ["BRAILLE LINE:  'gtk3-demo application Interactive Dialog dialog Entry 2 Again $l'",
     "     VISIBLE:  'Entry 2 Again $l', cursor=14",
     "BRAILLE LINE:  'gtk3-demo application Interactive Dialog dialog Entry 2 Again $l'",
     "     VISIBLE:  'Entry 2 Again $l', cursor=14",
     "SPEECH OUTPUT: 'Entry 2 text.'",
     "SPEECH OUTPUT: 'Again selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Title bar",
    ["BRAILLE LINE:  'Interactive Dialog'",
     "     VISIBLE:  'Interactive Dialog', cursor=0",
     "SPEECH OUTPUT: 'Interactive Dialog'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
