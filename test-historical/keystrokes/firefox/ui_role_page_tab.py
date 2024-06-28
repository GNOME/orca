#!/usr/bin/python

"""Test of page tab output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(KeyComboAction("p"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Right Arrow to next page tab",
    ["BRAILLE LINE:  'Firefox application Print dialog Page Setup page tab'",
     "     VISIBLE:  'Page Setup page tab', cursor=1",
     "SPEECH OUTPUT: 'Page Setup page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right Arrow to next page tab",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab'",
     "     VISIBLE:  'Options page tab', cursor=1",
     "SPEECH OUTPUT: 'Options page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab'",
     "     VISIBLE:  'Options page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list.'",
     "SPEECH OUTPUT: 'Options page tab.'",
     "SPEECH OUTPUT: '[1-9] of [1-9]'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Left Arrow to previous page tab",
    ["BRAILLE LINE:  'Firefox application Print dialog Page Setup page tab'",
     "     VISIBLE:  'Page Setup page tab', cursor=1",
     "SPEECH OUTPUT: 'Page Setup page tab.'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
