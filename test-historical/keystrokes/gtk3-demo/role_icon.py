#!/usr/bin/python

"""Test of icon output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Images"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. bin icon",
    ["BRAILLE LINE:  'gtk3-demo application Icon View Basics frame layered pane bin icon'",
     "     VISIBLE:  'bin icon', cursor=1",
     "SPEECH OUTPUT: 'bin icon.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. bin icon Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Icon View Basics frame layered pane bin icon'",
     "     VISIBLE:  'bin icon', cursor=1",
     "SPEECH OUTPUT: 'Icon panel.'",
     "SPEECH OUTPUT: 'bin.'",
     "SPEECH OUTPUT: '1 of 20 items selected on 1 of 20.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. boot icon",
    ["BRAILLE LINE:  'gtk3-demo application Icon View Basics frame layered pane boot icon'",
     "     VISIBLE:  'boot icon', cursor=1",
     "SPEECH OUTPUT: 'boot icon.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "4. icon selection",
    ["BRAILLE LINE:  'gtk3-demo application Icon View Basics frame layered pane bin icon'",
     "     VISIBLE:  'bin icon', cursor=1",
     "SPEECH OUTPUT: 'bin icon.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "5. icon selection Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Icon View Basics frame layered pane bin icon'",
     "     VISIBLE:  'bin icon', cursor=1",
     "SPEECH OUTPUT: 'Icon panel.'",
     "SPEECH OUTPUT: 'bin.'",
     "SPEECH OUTPUT: '2 of 20 items selected on 1 of 20.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
