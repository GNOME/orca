#!/usr/bin/python

"""Test of Dojo combo box presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to the first combo box",
    ["BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  'US State test 1 (200% Courier fo', cursor=0",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=32",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font):'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'California'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C"))
sequence.append(utils.AssertPresentationAction(
    "2. Replace existing text with a 'C'",
    ["KNOWN ISSUE: It would be good to present the appearance of the popup so one knows there's something to Down arrow into.",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '(200% Courier font): C $l', cursor=23",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '(200% Courier font): C $l', cursor=23"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["KNOWN ISSUE: Too much braille updating",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=21",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=21",
     "BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  'ate test 1 (200% Courier font): ', cursor=32",
     "SPEECH OUTPUT: 'California'",
     "SPEECH OUTPUT: 'California'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: 'California'",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: 'California (CA)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow",
    ["BRAILLE LINE:  'Colorado (CO)'",
     "     VISIBLE:  'Colorado (CO)', cursor=1",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): Colorado $l'",
     "     VISIBLE:  'ate test 1 (200% Courier font): ', cursor=32",
     "SPEECH OUTPUT: 'Colorado (CO)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow",
    ["BRAILLE LINE:  'Connecticut (CT)'",
     "     VISIBLE:  'Connecticut (CT)', cursor=1",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): Connecticut $l'",
     "     VISIBLE:  'ate test 1 (200% Courier font): ', cursor=32",
     "SPEECH OUTPUT: 'Connecticut (CT)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down Arrow",
    ["BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  'ate test 1 (200% Courier font): ', cursor=32",
     "SPEECH OUTPUT: 'California (CA)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Up Arrow",
    ["BRAILLE LINE:  'Connecticut (CT)'",
     "     VISIBLE:  'Connecticut (CT)', cursor=1",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): Connecticut $l'",
     "     VISIBLE:  'ate test 1 (200% Courier font): ', cursor=32",
     "SPEECH OUTPUT: 'Connecticut (CT)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Up Arrow",
    ["BRAILLE LINE:  'Colorado (CO)'",
     "     VISIBLE:  'Colorado (CO)', cursor=1",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): Colorado $l'",
     "     VISIBLE:  'ate test 1 (200% Courier font): ', cursor=32",
     "SPEECH OUTPUT: 'Colorado (CO)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Up Arrow",
    ["BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  'ate test 1 (200% Courier font): ', cursor=32",
     "SPEECH OUTPUT: 'California (CA)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Basic Where Am I - Combo box expanded",
    ["BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'California (CA)'",
     "SPEECH OUTPUT: '1 of 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "11. Escape",
    ["BRAILLE LINE:  'US State test 1 (200% Courier font): California $l'",
     "     VISIBLE:  '(200% Courier font): California ', cursor=32",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font):'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'California'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
