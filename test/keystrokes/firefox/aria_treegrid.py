#!/usr/bin/python

"""Test of ARIA treegrid presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Navigate to the treegrid",
    ["BRAILLE LINE:  '+A Question of Love'",
     "     VISIBLE:  '+A Question of Love', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: '+A Question of Love'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["BRAILLE LINE:  '+A Question of Love'",
     "     VISIBLE:  '+A Question of Love', cursor=1",
     "BRAILLE LINE:  '+ Piece of Peace table cell'",
     "     VISIBLE:  '+ Piece of Peace table cell', cursor=1",
     "SPEECH OUTPUT: '+ Piece of Peace'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["BRAILLE LINE:  '+ International Law table cell'",
     "     VISIBLE:  '+ International Law table cell', cursor=1",
     "SPEECH OUTPUT: '+ International Law'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow",
    ["BRAILLE LINE:  '+ Piece of Peace table cell'",
     "     VISIBLE:  '+ Piece of Peace table cell', cursor=1",
     "SPEECH OUTPUT: '+ Piece of Peace'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow",
    ["BRAILLE LINE:  '+A Question of Love table cell'",
     "     VISIBLE:  '+A Question of Love table cell', cursor=1",
     "SPEECH OUTPUT: '+A Question of Love'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. basic whereAmI",
    ["BRAILLE LINE:  '+A Question of Love table cell'",
     "     VISIBLE:  '+A Question of Love table cell', cursor=1",
     "SPEECH OUTPUT: 'table row ISBN +A Question of Love'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "7. Space to expand the current item",
    ["BRAILLE LINE:  '-A Question of Love table row'",
     "     VISIBLE:  '-A Question of Love table row', cursor=1",
     "BRAILLE LINE:  '-A Question of Love table cell'",
     "     VISIBLE:  '-A Question of Love table cell', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. basic whereAmI",
    ["BRAILLE LINE:  '-A Question of Love table cell'",
     "     VISIBLE:  '-A Question of Love table cell', cursor=1",
     "SPEECH OUTPUT: 'table row ISBN -A Question of Love'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow into child",
    ["BRAILLE LINE:  '978-3-453-40540-0 table cell'",
     "     VISIBLE:  '978-3-453-40540-0 table cell', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "10. Right Arrow in child",
    ["BRAILLE LINE:  'Nora Roberts table cell'",
     "     VISIBLE:  'Nora Roberts table cell', cursor=1",
     "SPEECH OUTPUT: 'Nora Roberts'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Right Arrow in child",
    ["BRAILLE LINE:  '$ 9.99 table cell'",
     "     VISIBLE:  '$ 9.99 table cell', cursor=1",
     "SPEECH OUTPUT: '$ 9.99'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Left Arrow in child",
    ["BRAILLE LINE:  'Nora Roberts table cell'",
     "     VISIBLE:  'Nora Roberts table cell', cursor=1",
     "SPEECH OUTPUT: 'Nora Roberts'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Left Arrow in child",
    ["BRAILLE LINE:  '978-3-453-40540-0 table cell'",
     "     VISIBLE:  '978-3-453-40540-0 table cell', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Up Arrow back to parent",
    ["BRAILLE LINE:  '-A Question of Love table cell'",
     "     VISIBLE:  '-A Question of Love table cell', cursor=1",
     "SPEECH OUTPUT: '-A Question of Love'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
