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
    "1. vertical splitter",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 84 vertical splitter'",
     "     VISIBLE:  '84 vertical splitter', cursor=1",
     "SPEECH OUTPUT: 'vertical splitter 84'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. vertical splitter increment value",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 85 vertical splitter'",
     "     VISIBLE:  '85 vertical splitter', cursor=1",
     "SPEECH OUTPUT: '85'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. vertical splitter Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 85 vertical splitter'",
     "     VISIBLE:  '85 vertical splitter', cursor=1",
     "SPEECH OUTPUT: 'vertical splitter 85'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. vertical splitter decrement value",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 84 vertical splitter'",
     "     VISIBLE:  '84 vertical splitter', cursor=1",
     "SPEECH OUTPUT: '84'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F8"))
sequence.append(utils.AssertPresentationAction(
    "5. horizontal splitter",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 60 horizontal splitter'",
     "     VISIBLE:  '60 horizontal splitter', cursor=1",
     "SPEECH OUTPUT: 'horizontal splitter 60'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. horizontal splitter increment value",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 61 horizontal splitter'",
     "     VISIBLE:  '61 horizontal splitter', cursor=1",
     "SPEECH OUTPUT: '61'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. horizontal splitter Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 61 horizontal splitter'",
     "     VISIBLE:  '61 horizontal splitter', cursor=1",
     "SPEECH OUTPUT: 'horizontal splitter 61'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. horizontal splitter decrement value",
    ["BRAILLE LINE:  'gtk3-demo application Paned Widgets frame 60 horizontal splitter'",
     "     VISIBLE:  '60 horizontal splitter', cursor=1",
     "SPEECH OUTPUT: '60'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
