#!/usr/bin/python

"""Test of line navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Hello world'",
     "     VISIBLE:  'Hello world', cursor=1",
     "SPEECH OUTPUT: 'Hello world'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Paragraph 1'",
     "     VISIBLE:  'Paragraph 1', cursor=1",
     "SPEECH OUTPUT: 'link Paragraph 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Paragraph 2'",
     "     VISIBLE:  'Paragraph 2', cursor=1",
     "SPEECH OUTPUT: 'link Paragraph 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Goodbye world'",
     "     VISIBLE:  'Goodbye world', cursor=1",
     "SPEECH OUTPUT: 'Goodbye world'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'Paragraph 2'",
     "     VISIBLE:  'Paragraph 2', cursor=1",
     "SPEECH OUTPUT: 'link Paragraph 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'Paragraph 1'",
     "     VISIBLE:  'Paragraph 1', cursor=1",
     "SPEECH OUTPUT: 'link Paragraph 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Hello world'",
     "     VISIBLE:  'Hello world', cursor=1",
     "SPEECH OUTPUT: 'Hello world'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
