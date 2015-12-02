#!/usr/bin/python

"""Test of line navigation in a table with a caption."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Below is a table, with some sample table data'",
     "     VISIBLE:  'Below is a table, with some samp', cursor=1",
     "SPEECH OUTPUT: 'Below is a table, with some sample table data'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down into the caption",
    ["BRAILLE LINE:  'this is a caption for this table caption'",
     "     VISIBLE:  'this is a caption for this table', cursor=1",
     "SPEECH OUTPUT: 'this is a caption for this table caption'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down to headers row",
    ["BRAILLE LINE:  'col1 col2 col3'",
     "     VISIBLE:  'col1 col2 col3', cursor=1",
     "SPEECH OUTPUT: 'col1 column header'",
     "SPEECH OUTPUT: 'col2 column header'",
     "SPEECH OUTPUT: 'col3 column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down to first data row",
    ["BRAILLE LINE:  '1 2 3'",
     "     VISIBLE:  '1 2 3', cursor=1",
     "SPEECH OUTPUT: '1.'",
     "SPEECH OUTPUT: '2.'",
     "SPEECH OUTPUT: '3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down to second data row",
    ["BRAILLE LINE:  '4 5 6'",
     "     VISIBLE:  '4 5 6', cursor=1",
     "SPEECH OUTPUT: '4.'",
     "SPEECH OUTPUT: '5.'",
     "SPEECH OUTPUT: '6.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down to third data row",
    ["BRAILLE LINE:  '7 8 9'",
     "     VISIBLE:  '7 8 9', cursor=1",
     "SPEECH OUTPUT: '7.'",
     "SPEECH OUTPUT: '8.'",
     "SPEECH OUTPUT: '9.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down out of the table",
    ["BRAILLE LINE:  'hope the table looks pretty'",
     "     VISIBLE:  'hope the table looks pretty', cursor=1",
     "SPEECH OUTPUT: 'hope the table looks pretty'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up into table's third data row",
    ["BRAILLE LINE:  '7 8 9'",
     "     VISIBLE:  '7 8 9', cursor=1",
     "SPEECH OUTPUT: '7.'",
     "SPEECH OUTPUT: '8.'",
     "SPEECH OUTPUT: '9.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up to second data row",
    ["BRAILLE LINE:  '4 5 6'",
     "     VISIBLE:  '4 5 6', cursor=1",
     "SPEECH OUTPUT: '4.'",
     "SPEECH OUTPUT: '5.'",
     "SPEECH OUTPUT: '6.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up to first data row",
    ["BRAILLE LINE:  '1 2 3'",
     "     VISIBLE:  '1 2 3', cursor=1",
     "SPEECH OUTPUT: '1.'",
     "SPEECH OUTPUT: '2.'",
     "SPEECH OUTPUT: '3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up to headers row",
    ["BRAILLE LINE:  'col1 col2 col3'",
     "     VISIBLE:  'col1 col2 col3', cursor=1",
     "SPEECH OUTPUT: 'col1 column header'",
     "SPEECH OUTPUT: 'col2 column header'",
     "SPEECH OUTPUT: 'col3 column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up to the caption",
    ["BRAILLE LINE:  'this is a caption for this table caption'",
     "     VISIBLE:  'this is a caption for this table', cursor=1",
     "SPEECH OUTPUT: 'this is a caption for this table caption'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up to the first line of text",
    ["BRAILLE LINE:  'Below is a table, with some sample table data'",
     "     VISIBLE:  'Below is a table, with some samp', cursor=1",
     "SPEECH OUTPUT: 'Below is a table, with some sample table data'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
