#!/usr/bin/python

"""Test of slider output using custom program."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. slider Where Am I",
    ["BRAILLE LINE:  'slider application Slider frame Some slider: 0 slider'",
     "     VISIBLE:  'Some slider: 0 slider', cursor=1",
     "SPEECH OUTPUT: 'Some slider:'",
     "SPEECH OUTPUT: 'slider 0 0 percent.'",
     "SPEECH OUTPUT: 'Alt+S'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Increment value",
    ["BRAILLE LINE:  'slider application Slider frame Some slider: 1 slider'",
     "     VISIBLE:  'Some slider: 1 slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. slider Where Am I",
    ["BRAILLE LINE:  'slider application Slider frame Some slider: 1 slider'",
     "     VISIBLE:  'Some slider: 1 slider', cursor=1",
     "SPEECH OUTPUT: 'Some slider:'",
     "SPEECH OUTPUT: 'slider 1 12 percent.'",
     "SPEECH OUTPUT: 'Alt+S'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Decrement value",
    ["BRAILLE LINE:  'slider application Slider frame Some slider: 0 slider'",
     "     VISIBLE:  'Some slider: 0 slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "5. slider Where Am I",
    ["BRAILLE LINE:  'slider application Slider frame Some slider: 0 slider'",
     "     VISIBLE:  'Some slider: 0 slider', cursor=1",
     "SPEECH OUTPUT: 'Some slider:'",
     "SPEECH OUTPUT: 'slider 0 0 percent.'",
     "SPEECH OUTPUT: 'Alt+S'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
