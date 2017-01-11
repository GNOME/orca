#!/usr/bin/python

"""Test to verify table message presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("<Control>F12"))
sequence.append(PauseAction(1000))

sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down arrow to enter the table",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'A1 B1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down arrow to next row of the table",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'A2 B2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down arrow to exit the table",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up arrow to enter the table",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'A2 B2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to move to last cell of the table",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'End of table.'",
     "SPEECH OUTPUT: 'blank B2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to insert a new row in the table",
    ["BRAILLE LINE:  'Row inserted at the end of the table.'",
     "     VISIBLE:  'Row inserted at the end of the t', cursor=0",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Row inserted at the end of the table.' voice=system",
     "SPEECH OUTPUT: 'blank A3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Z"))
sequence.append(utils.AssertPresentationAction(
    "7. Ctrl+Z to undo that insertion",
    ["BRAILLE LINE:  'undo'",
     "     VISIBLE:  'undo', cursor=0",
     "BRAILLE LINE:  'Last row deleted.'",
     "     VISIBLE:  'Last row deleted.', cursor=0",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'undo' voice=system",
     "SPEECH OUTPUT: 'Last row deleted.' voice=system",
     "SPEECH OUTPUT: 'End of table.'",
     "SPEECH OUTPUT: 'A2 B2.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
