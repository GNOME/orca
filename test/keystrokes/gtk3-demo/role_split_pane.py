#!/usr/bin/python

"""Test of split pane output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Paned Widgets"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F8"))
sequence.append(utils.AssertPresentationAction(
    "1. Split pane",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 89 split pane'",
     "     VISIBLE:  '89 split pane', cursor=1",
     "SPEECH OUTPUT: 'split pane 89'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Split pane increment value",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 90 split pane'",
     "     VISIBLE:  '90 split pane', cursor=1",
     "SPEECH OUTPUT: '90'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Split pane Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 90 split pane'",
     "     VISIBLE:  '90 split pane', cursor=1",
     "SPEECH OUTPUT: 'split pane 90'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Split pane decrement value",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 89 split pane'",
     "     VISIBLE:  '89 split pane', cursor=1",
     "SPEECH OUTPUT: '89'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
