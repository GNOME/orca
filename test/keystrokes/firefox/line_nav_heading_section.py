#!/usr/bin/python

"""Test of line navigation on a page with headings in sections."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Heading 1. h1'",
     "     VISIBLE:  'Heading 1. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 1. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Heading 2. h1'",
     "     VISIBLE:  'Heading 2. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 2. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'sect 1'",
     "     VISIBLE:  'sect 1', cursor=1",
     "SPEECH OUTPUT: 'sect 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Heading 3. h1'",
     "     VISIBLE:  'Heading 3. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 3. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'sect 2'",
     "     VISIBLE:  'sect 2', cursor=1",
     "SPEECH OUTPUT: 'sect 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Heading 4. h1'",
     "     VISIBLE:  'Heading 4. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 4. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'sect 3'",
     "     VISIBLE:  'sect 3', cursor=1",
     "SPEECH OUTPUT: 'sect 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'Heading 5. h1'",
     "     VISIBLE:  'Heading 5. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 5. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Heading 6. h1'",
     "     VISIBLE:  'Heading 6. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 6. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'Heading 5. h1'",
     "     VISIBLE:  'Heading 5. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 5. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'sect 3'",
     "     VISIBLE:  'sect 3', cursor=1",
     "SPEECH OUTPUT: 'sect 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'Heading 4. h1'",
     "     VISIBLE:  'Heading 4. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 4. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'sect 2'",
     "     VISIBLE:  'sect 2', cursor=1",
     "SPEECH OUTPUT: 'sect 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'Heading 3. h1'",
     "     VISIBLE:  'Heading 3. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 3. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'sect 1'",
     "     VISIBLE:  'sect 1', cursor=1",
     "SPEECH OUTPUT: 'sect 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'Heading 2. h1'",
     "     VISIBLE:  'Heading 2. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 2. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  'Heading 1. h1'",
     "     VISIBLE:  'Heading 1. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 1. heading level 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
