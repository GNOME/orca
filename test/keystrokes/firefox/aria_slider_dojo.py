#!/usr/bin/python

"""Test of Dojo slider presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first slider",
    ["KNOWN ISSUE: Why are we not displaying the value after focus mode?",
     "BRAILLE LINE:  'slider 1 10 slider'",
     "     VISIBLE:  'slider 1 10 slider', cursor=0",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'slider 1'",
     "SPEECH OUTPUT: 'slider 10'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Increment first slider",
    ["KNOWN ISSUE: This is the value exposed to us so we're passing it along as-is.",
     "BRAILLE LINE:  'slider 1 10 slider'",
     "     VISIBLE:  'slider 1 10 slider', cursor=0",
     "BRAILLE LINE:  'slider 1 10.238095238095237 slider'",
     "     VISIBLE:  'slider 1 10.238095238095237 slid', cursor=1",
     "SPEECH OUTPUT: '10.238095238095237'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Increment first slider",
    ["BRAILLE LINE:  'slider 1 10.476190476190476 slider'",
     "     VISIBLE:  'slider 1 10.476190476190476 slid', cursor=1",
     "SPEECH OUTPUT: '10.476190476190476'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Decrement first slider",
    ["BRAILLE LINE:  'slider 1 10.238095238095237 slider'",
     "     VISIBLE:  'slider 1 10.238095238095237 slid', cursor=1",
     "SPEECH OUTPUT: '10.238095238095237'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Decrement first slider",
    ["BRAILLE LINE:  'slider 1 10 slider'",
     "     VISIBLE:  'slider 1 10 slider', cursor=1",
     "SPEECH OUTPUT: '10'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Move to entry",
    ["BRAILLE LINE:  'Slider1 Value: 10.0% $l rdonly'",
     "     VISIBLE:  'Slider1 Value: 10.0% $l rdonly', cursor=21",
     "BRAILLE LINE:  'Slider1 Value: 10.0% $l rdonly'",
     "     VISIBLE:  'Slider1 Value: 10.0% $l rdonly', cursor=21",
     "SPEECH OUTPUT: 'Slider1 Value:",
     "SPEECH OUTPUT: 'read only entry'",
     "SPEECH OUTPUT: '10.0%'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Move to button",
    ["BRAILLE LINE:  'Disable previous slider push button'",
     "     VISIBLE:  'Disable previous slider push but', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Disable previous slider'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Tab to second slider",
    ["BRAILLE LINE:  'Disable previous slider push button'",
     "     VISIBLE:  'Disable previous slider push but', cursor=1",
     "BRAILLE LINE:  'slider 2 10 slider'",
     "     VISIBLE:  'slider 2 10 slider', cursor=0",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'slider 2'",
     "SPEECH OUTPUT: 'slider 10'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Increment second slider",
    ["BRAILLE LINE:  'slider 2 10 slider'",
     "     VISIBLE:  'slider 2 10 slider', cursor=0",
     "BRAILLE LINE:  'slider 2 20 slider'",
     "     VISIBLE:  'slider 2 20 slider', cursor=1",
     "SPEECH OUTPUT: '20'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Increment second slider",
    ["BRAILLE LINE:  'slider 2 30 slider'",
     "     VISIBLE:  'slider 2 30 slider', cursor=1",
     "SPEECH OUTPUT: '30'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Decrement second slider",
    ["BRAILLE LINE:  'slider 2 20 slider'",
     "     VISIBLE:  'slider 2 20 slider', cursor=1",
     "SPEECH OUTPUT: '20'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Decrement second slider",
    ["BRAILLE LINE:  'slider 2 10 slider'",
     "     VISIBLE:  'slider 2 10 slider', cursor=1",
     "SPEECH OUTPUT: '10'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
