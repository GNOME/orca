# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of the fix for bug 512303."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# Load the local test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction(utils.htmlURLPrefix + "table-caption.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Below is a table, with some sample table data'",
     "     VISIBLE:  'Below is a table, with some samp', cursor=1",
     "SPEECH OUTPUT: 'Below is a table, with some sample table data'"]))

########################################################################
# Down Arrow to the bottom.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'this is a caption for this table caption'",
     "     VISIBLE:  'this is a caption for this table', cursor=1",
     "SPEECH OUTPUT: 'this is a caption for this table'",
     "SPEECH OUTPUT: 'caption'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'col1 col2 col3'",
     "     VISIBLE:  'col1 col2 col3', cursor=1",
     "SPEECH OUTPUT: 'col1'",
     "SPEECH OUTPUT: 'column header'",
     "SPEECH OUTPUT: 'col2'",
     "SPEECH OUTPUT: 'column header'",
     "SPEECH OUTPUT: 'col3'",
     "SPEECH OUTPUT: 'column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '1 2 3'",
     "     VISIBLE:  '1 2 3', cursor=1",
     "SPEECH OUTPUT: '1'",
     "SPEECH OUTPUT: '2'",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '4 5 6'",
     "     VISIBLE:  '4 5 6', cursor=1",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: '6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '7 8 9'",
     "     VISIBLE:  '7 8 9', cursor=1",
     "SPEECH OUTPUT: '7'",
     "SPEECH OUTPUT: '8'",
     "SPEECH OUTPUT: '9'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'hope the table looks pretty'",
     "     VISIBLE:  'hope the table looks pretty', cursor=1",
     "SPEECH OUTPUT: 'hope the table looks pretty'"]))

########################################################################
# Up Arrow to the bottom.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '7 8 9'",
     "     VISIBLE:  '7 8 9', cursor=1",
     "SPEECH OUTPUT: '7'",
     "SPEECH OUTPUT: '8'",
     "SPEECH OUTPUT: '9'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '4 5 6'",
     "     VISIBLE:  '4 5 6', cursor=1",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: '6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '1 2 3'",
     "     VISIBLE:  '1 2 3', cursor=1",
     "SPEECH OUTPUT: '1'",
     "SPEECH OUTPUT: '2'",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'col1 col2 col3'",
     "     VISIBLE:  'col1 col2 col3', cursor=1",
     "SPEECH OUTPUT: 'col1'",
     "SPEECH OUTPUT: 'column header'",
     "SPEECH OUTPUT: 'col2'",
     "SPEECH OUTPUT: 'column header'",
     "SPEECH OUTPUT: 'col3'",
     "SPEECH OUTPUT: 'column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'this is a caption for this table caption'",
     "     VISIBLE:  'this is a caption for this table', cursor=1",
     "SPEECH OUTPUT: 'this is a caption for this table'",
     "SPEECH OUTPUT: 'caption'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Below is a table, with some sample table data'",
     "     VISIBLE:  'Below is a table, with some samp', cursor=1",
     "SPEECH OUTPUT: 'Below is a table, with some sample table data'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
