#!/usr/bin/python

"""Test of line navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This is a test.'",
     "     VISIBLE:  'This is a test.', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'foo image h2'",
     "     VISIBLE:  'foo image h2', cursor=0",
     "SPEECH OUTPUT: 'foo'",
     "SPEECH OUTPUT: 'image link'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Joanmarie h2'",
     "     VISIBLE:  'Joanmarie h2', cursor=1",
     "SPEECH OUTPUT: 'Joanmarie'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Another test'",
     "     VISIBLE:  'Another test', cursor=1",
     "SPEECH OUTPUT: 'Another test'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Joanmarie h2'",
     "     VISIBLE:  'Joanmarie h2', cursor=1",
     "SPEECH OUTPUT: 'Joanmarie'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'foo image h2'",
     "     VISIBLE:  'foo image h2', cursor=0",
     "SPEECH OUTPUT: 'foo'",
     "SPEECH OUTPUT: 'image link'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'This is a test.'",
     "     VISIBLE:  'This is a test.', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
