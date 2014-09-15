#!/usr/bin/python

"""Test of UIUC grid presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to grid",
    ["KNOWN ISSUE: The braille is not correct here",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'Selected Sort Sel column push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. basic whereAmI",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'Selected Sort Sel column push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Move down into first data row",
    ["BRAILLE LINE:  'Sort Sel column'",
     "     VISIBLE:  'Sort Sel column', cursor=1",
     "SPEECH OUTPUT: 'Sort Sel column'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Move right in first data row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'Sort Sel column'",
     "     VISIBLE:  'Sort Sel column', cursor=2",
     "SPEECH OUTPUT: 'o'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Move right in first data row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'Sort Sel column'",
     "     VISIBLE:  'Sort Sel column', cursor=3",
     "SPEECH OUTPUT: 'r'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Move right in first data row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'Sort Sel column'",
     "     VISIBLE:  'Sort Sel column', cursor=4",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Move down to third row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'Msg '",
     "     VISIBLE:  'Msg ', cursor=1",
     "SPEECH OUTPUT: 'Msg'",
     "SPEECH OUTPUT: 'image clickable'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
