#!/usr/bin/python

"""Test of ARIA treegrid presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Navigate to the treegrid",
    ["BRAILLE LINE:  '+A Question of Love table cell'",
     "     VISIBLE:  '+A Question of Love table cell', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: '+A Question of Love.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["BRAILLE LINE:  '+A Question of Love table cell'",
     "     VISIBLE:  '+A Question of Love table cell', cursor=1",
     "BRAILLE LINE:  '+ Piece of Peace table row'",
     "     VISIBLE:  '+ Piece of Peace table row', cursor=1",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: '+ Piece of Peace table row tree level 1 not selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["BRAILLE LINE:  '+ International Law table row'",
     "     VISIBLE:  '+ International Law table row', cursor=1",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: '+ International Law table row tree level 1 not selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow",
    ["BRAILLE LINE:  '+ Piece of Peace table row'",
     "     VISIBLE:  '+ Piece of Peace table row', cursor=1",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: '+ Piece of Peace table row tree level 1 not selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow",
    ["BRAILLE LINE:  '+A Question of Love table row'",
     "     VISIBLE:  '+A Question of Love table row', cursor=1",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: '+A Question of Love table row tree level 1 not selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. basic whereAmI",
    ["BRAILLE LINE:  '+A Question of Love table row'",
     "     VISIBLE:  '+A Question of Love table row', cursor=1",
     "SPEECH OUTPUT: 'table row.'",
     "SPEECH OUTPUT: 'ISBN.'",
     "SPEECH OUTPUT: '+A Question of Love.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "7. Space to expand the current item",
    ["BRAILLE LINE:  '-A Question of Love table row'",
     "     VISIBLE:  '-A Question of Love table row', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. basic whereAmI",
    ["BRAILLE LINE:  '-A Question of Love table row'",
     "     VISIBLE:  '-A Question of Love table row', cursor=1",
     "SPEECH OUTPUT: 'table row.'",
     "SPEECH OUTPUT: 'ISBN.'",
     "SPEECH OUTPUT: '-A Question of Love.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow into child",
    ["BRAILLE LINE:  '978-3-453-40540-0 Nora Roberts $ 9.99 table row'",
     "     VISIBLE:  '978-3-453-40540-0 Nora Roberts $', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0 Nora Roberts $ 9.99 table row tree level 2 not selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "10. Right Arrow in child",
    ["KNOWN ISSUE: We should only be presenting the cell",
     "BRAILLE LINE:  '978-3-453-40540-0 Nora Roberts $ 9.99 table row'",
     "     VISIBLE:  '978-3-453-40540-0 Nora Roberts $', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0 Nora Roberts $ 9.99 table row tree level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Right Arrow in child",
    ["BRAILLE LINE:  '978-3-453-40540-0 Nora Roberts $ 9.99 table row'",
     "     VISIBLE:  '978-3-453-40540-0 Nora Roberts $', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0 Nora Roberts $ 9.99 table row tree level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Left Arrow in child",
    ["BRAILLE LINE:  '978-3-453-40540-0 Nora Roberts $ 9.99 table row'",
     "     VISIBLE:  '978-3-453-40540-0 Nora Roberts $', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0 Nora Roberts $ 9.99 table row tree level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Left Arrow in child",
    ["BRAILLE LINE:  '978-3-453-40540-0 Nora Roberts $ 9.99 table row'",
     "     VISIBLE:  '978-3-453-40540-0 Nora Roberts $', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0 Nora Roberts $ 9.99 table row tree level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Up Arrow back to parent",
    ["BRAILLE LINE:  '-A Question of Love table row'",
     "     VISIBLE:  '-A Question of Love table row', cursor=1",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: '-A Question of Love table row tree level 1 not selected.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
