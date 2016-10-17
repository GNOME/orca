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
    ["BRAILLE LINE:  'Templates dialog All Categories combo box'",
     "     VISIBLE:  'All Categories combo box', cursor=1",
     "SPEECH OUTPUT: 'All Categories combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to list item",
    ["KNOWN ISSUE: When the list gains focus, we get no events for it or the selected list item.",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right to next list item",
    ["BRAILLE LINE:  'Templates dialog list \"Modern\" business letter list item'",
     "     VISIBLE:  '\"Modern\" business letter list it', cursor=1",
     "SPEECH OUTPUT: '\"Modern\" business letter.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Left to previous list item",
    ["BRAILLE LINE:  'Templates dialog list \"Moderate\" business letter list item'",
     "     VISIBLE:  '\"Moderate\" business letter list ', cursor=1",
     "SPEECH OUTPUT: '\"Moderate\" business letter.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
