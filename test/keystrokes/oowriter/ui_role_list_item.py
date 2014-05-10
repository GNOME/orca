#!/usr/bin/python

"""Test to verify presentation of selectable list items."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control><Shift>n"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to list item",
    ["KNOWN ISSUE: We are presenting nothing here",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right to next list item",
    ["BRAILLE LINE:  'soffice application Template Manager frame Template Manager dialog Drawings page tab list Presentation Backgrounds list item'",
     "     VISIBLE:  'Presentation Backgrounds list it', cursor=1",
     "SPEECH OUTPUT: 'Presentation Backgrounds'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Left to previous list item",
    ["BRAILLE LINE:  'soffice application Template Manager frame Template Manager dialog Drawings page tab list My Templates list item'",
     "     VISIBLE:  'My Templates list item', cursor=1",
     "SPEECH OUTPUT: 'My Templates'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
