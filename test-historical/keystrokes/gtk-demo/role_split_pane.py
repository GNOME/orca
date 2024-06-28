#!/usr/bin/python

"""Test of split pane output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Paned Widgets"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F8"))
sequence.append(utils.AssertPresentationAction(
    "1. vertical splitter",
    ["BRAILLE LINE:  'gtk-demo application Panes frame 60 vertical splitter'",
     "     VISIBLE:  '60 vertical splitter', cursor=1",
     "SPEECH OUTPUT: 'vertical splitter 60'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. vertical splitter increment value",
    ["BRAILLE LINE:  'gtk-demo application Panes frame 61 vertical splitter'",
     "     VISIBLE:  '61 vertical splitter', cursor=1",
     "SPEECH OUTPUT: '61'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. vertical splitter Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Panes frame 61 vertical splitter'",
     "     VISIBLE:  '61 vertical splitter', cursor=1",
     "SPEECH OUTPUT: 'vertical splitter 61'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. vertical splitter decrement value",
    ["BRAILLE LINE:  'gtk-demo application Panes frame 60 vertical splitter'",
     "     VISIBLE:  '60 vertical splitter', cursor=1",
     "SPEECH OUTPUT: '60'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
