#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'document frame'",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["KNOWN ISSUE: We're stuck here",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'document frame'",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["KNOWN ISSUE: We're stuck here",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'document frame'",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "6. Bottom of file",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=6",
     "SPEECH OUTPUT: 'Line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'document frame'",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
