#!/usr/bin/python

"""Test of HTML list item whereAmI presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  '• Not in a paragraph'",
     "     VISIBLE:  '• Not in a paragraph', cursor=1",
     "SPEECH OUTPUT: '• Not in a paragraph.'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I next item",
    ["BRAILLE LINE:  '• In a paragraph'",
     "     VISIBLE:  '• In a paragraph', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: '• In a paragraph.'",
     "SPEECH OUTPUT: '2 of 4.'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I next item",
    ["BRAILLE LINE:  '• In a section'",
     "     VISIBLE:  '• In a section', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: '• In a section.'",
     "SPEECH OUTPUT: '3 of 4.'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Basic Where Am I next item",
    ["BRAILLE LINE:  '1. A nested list item, not in a paragraph LEVEL 1'",
     "     VISIBLE:  '1. A nested list item, not in a ', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: '1. A nested list item, not in a paragraph.'",
     "SPEECH OUTPUT: '1 of 3.'",
     "SPEECH OUTPUT: 'Nesting level 1.'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "5. Basic Where Am I next item",
    ["BRAILLE LINE:  '2. A nested list item, in a paragraph LEVEL 1'",
     "     VISIBLE:  '2. A nested list item, in a para', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: '2. A nested list item, in a paragraph.'",
     "SPEECH OUTPUT: '2 of 3.'",
     "SPEECH OUTPUT: 'Nesting level 1.'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Basic Where Am I next item",
    ["BRAILLE LINE:  '3. A nested list item, in a section LEVEL 1'",
     "     VISIBLE:  '3. A nested list item, in a sect', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: '3. A nested list item, in a section.'",
     "SPEECH OUTPUT: '3 of 3.'",
     "SPEECH OUTPUT: 'Nesting level 1.'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. Basic Where Am I next item",
    ["BRAILLE LINE:  '• In a paragraph that's in a section'",
     "     VISIBLE:  '• In a paragraph that's in a sec', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: '• In a paragraph that's in a section.'",
     "SPEECH OUTPUT: '4 of 4.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
