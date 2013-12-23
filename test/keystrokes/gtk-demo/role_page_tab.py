#!/usr/bin/python

"""Test of page tab output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Printing"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "General page tab",
    ["BRAILLE LINE:  'gtk-demo application Print dialog'",
     "     VISIBLE:  'Print dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Print dialog General page tab'",
     "     VISIBLE:  'General page tab', cursor=1",
     "SPEECH OUTPUT: 'Print Range Copies'",
     "SPEECH OUTPUT: 'General page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "General page tab Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Print dialog General page tab'",
     "     VISIBLE:  'General page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list'",
     "SPEECH OUTPUT: 'General'",
     "SPEECH OUTPUT: 'page tab 1 of 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Page Setup page tab",
    ["BRAILLE LINE:  'gtk-demo application Print dialog Page Setup page tab'",
     "     VISIBLE:  'Page Setup page tab', cursor=1",
     "SPEECH OUTPUT: 'Page Setup page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Page Setup page tab Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Print dialog Page Setup page tab'",
     "     VISIBLE:  'Page Setup page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list'",
     "SPEECH OUTPUT: 'Page Setup'",
     "SPEECH OUTPUT: 'page tab 2 of 5'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
