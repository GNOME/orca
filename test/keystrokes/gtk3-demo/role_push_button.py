#!/usr/bin/python

"""Test of push button output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Button Boxes"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. OK push button",
    ["BRAILLE LINE:  'gtk3-demo application Button Boxes frame'",
     "     VISIBLE:  'Button Boxes frame', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Button Boxes frame Horizontal Button Boxes panel Spread panel OK push button'",
     "     VISIBLE:  'OK push button', cursor=1",
     "SPEECH OUTPUT: 'Button Boxes frame'",
     "SPEECH OUTPUT: 'Horizontal Button Boxes panel.'",
     "SPEECH OUTPUT: 'Spread panel.'",
     "SPEECH OUTPUT: 'OK push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. OK push button Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Button Boxes frame Horizontal Button Boxes panel Spread panel OK push button'",
     "     VISIBLE:  'OK push button', cursor=1",
     "SPEECH OUTPUT: 'OK push button"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Cancel push button",
    ["BRAILLE LINE:  'gtk3-demo application Button Boxes frame Horizontal Button Boxes panel Spread panel Cancel push button'",
     "     VISIBLE:  'Cancel push button', cursor=1",
     "SPEECH OUTPUT: 'Cancel push button'"]))

sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. OK Edge button",
    ["BRAILLE LINE:  'gtk3-demo application Button Boxes frame Horizontal Button Boxes panel Edge panel OK push button'",
     "     VISIBLE:  'OK push button', cursor=1",
     "SPEECH OUTPUT: 'Edge panel.'",
     "SPEECH OUTPUT: 'OK push button'"]))

sequence.append(KeyComboAction("<Alt>F4", 500))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
