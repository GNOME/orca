#!/usr/bin/python

"""Test to verify presentation of selectable list items."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control><Shift>n"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to combo box",
    ["BRAILLE LINE:  'soffice application Templates dialog All Categories combo box'",
     "     VISIBLE:  'All Categories combo box', cursor=1",
     "SPEECH OUTPUT: 'Filter by Category All Categories combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to list item",
    ["BRAILLE LINE:  'soffice application Templates dialog Template List panel list Modern business letter sans-serif list item'",
     "     VISIBLE:  'Modern business letter sans-seri', cursor=1",
     "SPEECH OUTPUT: 'Template List panel.'",
     "SPEECH OUTPUT: 'List with 7 items.'",
     "SPEECH OUTPUT: 'Modern business letter sans-serif.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right to next list item",
    ["BRAILLE LINE:  'soffice application Templates dialog Template List panel list Modern business letter serif list item'",
     "     VISIBLE:  'Modern business letter serif lis', cursor=1",
     "SPEECH OUTPUT: 'Modern business letter serif.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Left to previous list item",
    ["BRAILLE LINE:  'soffice application Templates dialog Template List panel list Modern business letter sans-serif list item'",
     "     VISIBLE:  'Modern business letter sans-seri', cursor=1",
     "SPEECH OUTPUT: 'Modern business letter sans-serif.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
