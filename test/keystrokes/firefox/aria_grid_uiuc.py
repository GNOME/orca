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
    ["BRAILLE LINE:  'SelSort Sel column Msg'",
     "     VISIBLE:  'SelSort Sel column Msg', cursor=0",
     "SPEECH OUTPUT: 'Selected Sort Sel column push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. basic whereAmI",
    ["BRAILLE LINE:  'SelSort Sel column Msg'",
     "     VISIBLE:  'SelSort Sel column Msg', cursor=0",
     "SPEECH OUTPUT: 'Selected Sort Sel column'",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Move down into first data row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'SelSort Sel column Msg'",
     "     VISIBLE:  'SelSort Sel column Msg', cursor=4",
     "SPEECH OUTPUT: 'Sel'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'Sort Sel column'",
     "SPEECH OUTPUT: 'Msg'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Move right in first data row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'SelSort Sel column Msg'",
     "     VISIBLE:  'SelSort Sel column Msg', cursor=5",
     "SPEECH OUTPUT: 'o'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Move right in first data row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'SelSort Sel column Msg'",
     "     VISIBLE:  'SelSort Sel column Msg', cursor=6",
     "SPEECH OUTPUT: 'r'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Move right in first data row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'SelSort Sel column Msg'",
     "     VISIBLE:  'SelSort Sel column Msg', cursor=7",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Move down to third row",
    ["KNOWN ISSUE: It appears we are not treating this as an ARIA widget",
     "BRAILLE LINE:  'SelSort Sel column Msg'",
     "     VISIBLE:  'SelSort Sel column Msg', cursor=20",
     "SPEECH OUTPUT: 'Sel'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'Sort Sel column'",
     "SPEECH OUTPUT: 'Msg'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'clickable'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
