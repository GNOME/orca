#!/usr/bin/python

"""Test of page summary"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("6"))
sequence.append(utils.AssertPresentationAction(
    "1. Navigate to 'This is a Heading 6.'",
    ["BRAILLE LINE:  'This is a Heading 6. h6'",
     "     VISIBLE:  'This is a Heading 6. h6', cursor=1",
     "SPEECH OUTPUT: 'This is a Heading 6. heading level 6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(5000))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I for page summary info",
    ["BRAILLE LINE:  'This is a Heading 6. h6'",
     "     VISIBLE:  'This is a Heading 6. h6', cursor=1",
     "BRAILLE LINE:  'This is a Heading 6. h6'",
     "     VISIBLE:  'This is a Heading 6. h6', cursor=1",
     "SPEECH OUTPUT: 'heading level 6.'",
     "SPEECH OUTPUT: 'This is a Heading 6.'",
     "SPEECH OUTPUT: 'Page has 0 landmarks, 14 headings, 3 forms, 43 tables, 0 visited links, 11 unvisited links.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
