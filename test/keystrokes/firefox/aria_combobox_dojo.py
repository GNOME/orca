#!/usr/bin/python

"""Test of Dojo combo box presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to the first combo box",
    ["BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=32",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=32",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font): entry California selected'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C"))
sequence.append(utils.AssertPresentationAction(
    "2. Replace existing text with a 'C'",
    ["BRAILLE LINE:  'US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '(200% Courier font): C $l', cursor=23",
     "BRAILLE LINE:  'US State test 1 (200% Courier font):'",
     "     VISIBLE:  'US State test 1 (200% Courier fo', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["BRAILLE LINE:  'C alifornia (CA)'",
     "     VISIBLE:  'C alifornia (CA)', cursor=1",
     "SPEECH OUTPUT: 'California menu'",
     "SPEECH OUTPUT: 'C alifornia (CA)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow",
    ["BRAILLE LINE:  'C olorado (CO)'",
     "     VISIBLE:  'C olorado (CO)', cursor=1",
     "SPEECH OUTPUT: 'C olorado (CO)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow",
    ["BRAILLE LINE:  'C onnecticut (CT)'",
     "     VISIBLE:  'C onnecticut (CT)', cursor=1",
     "SPEECH OUTPUT: 'C onnecticut (CT)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down Arrow",
    ["BRAILLE LINE:  'C alifornia (CA)'",
     "     VISIBLE:  'C alifornia (CA)', cursor=1",
     "SPEECH OUTPUT: 'C alifornia (CA)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Up Arrow",
    ["BRAILLE LINE:  'C onnecticut (CT)'",
     "     VISIBLE:  'C onnecticut (CT)', cursor=1",
     "SPEECH OUTPUT: 'C onnecticut (CT)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Up Arrow",
    ["BRAILLE LINE:  'C olorado (CO)'",
     "     VISIBLE:  'C olorado (CO)', cursor=1",
     "SPEECH OUTPUT: 'C olorado (CO)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Up Arrow",
    ["BRAILLE LINE:  'C alifornia (CA)'",
     "     VISIBLE:  'C alifornia (CA)', cursor=1",
     "SPEECH OUTPUT: 'C alifornia (CA)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Basic Where Am I - Combo box expanded",
    ["BRAILLE LINE:  'C alifornia (CA)'",
     "     VISIBLE:  'C alifornia (CA)', cursor=1",
     "SPEECH OUTPUT: 'California menu'",
     "SPEECH OUTPUT: 'panel C alifornia (CA) 1 of 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "11. Escape",
    ["BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=32",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font): entry California selected'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
