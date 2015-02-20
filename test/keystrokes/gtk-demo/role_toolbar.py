#!/usr/bin/python

"""Test of toolbar output using."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Open push button'",
     "     VISIBLE:  'Open push button', cursor=1",
     "SPEECH OUTPUT: 'tool bar Open push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Open triangle toggle button",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame & y toggle button'",
     "     VISIBLE:  '& y toggle button', cursor=1",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Open triangle toggle button Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame & y toggle button'",
     "     VISIBLE:  '& y toggle button', cursor=1",
     "SPEECH OUTPUT: 'tool bar toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Next push button",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Quit push button'",
     "     VISIBLE:  'Quit push button', cursor=1",
     "SPEECH OUTPUT: 'Quit push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "5. Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Quit push button'",
     "     VISIBLE:  'Quit push button', cursor=1",
     "SPEECH OUTPUT: 'tool bar Quit push button'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
