#!/usr/bin/python

"""Test of Dojo combo box presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to the first combo box",
    ["BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  'font\): California $l', cursor=18",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font): editable combo box California selected.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C"))
sequence.append(utils.AssertPresentationAction(
    "2. Replace existing text with a 'C'",
    ["KNOWN ISSUE: The braille line is not quite right",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '(200% Courier font): C $l', cursor=23",
     "BRAILLE LINE:  'Selection deleted.'",
     "     VISIBLE:  'Selection deleted.', cursor=0",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  'e test 1 (200% Courier font): C ', cursor=32",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  'e test 1 (200% Courier font): C ', cursor=32",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): US State test 1 (200% Courier font): combo box'",
     "     VISIBLE:  'te test 1 (200% Courier font): U', cursor=32",
     "SPEECH OUTPUT: 'Selection deleted.' voice=system",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["BRAILLE LINE:  'C alifornia (CA)'",
     "     VISIBLE:  'C alifornia (CA)', cursor=1",
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
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'C alifornia (CA)'",
     "SPEECH OUTPUT: '1 of 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "11. Escape",
    ["BRAILLE LINE:  'US State test 1 (200% Courier font): US State test 1 (200% Courier font): combo box'",
     "     VISIBLE:  'te test 1 (200% Courier font): U', cursor=32",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=32",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font): editable combo box California selected.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
