#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["KNOWN ISSUE: It would be nice to not present the junk image",
     "BRAILLE LINE:  '< > I am a hidden label!   Check me! check box image'",
     "     VISIBLE:  '< > I am a hidden label!   Check', cursor=1",
     "SPEECH OUTPUT: 'I am a hidden label!   Check me! check box not checked'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["KNOWN ISSUE: We're double-presenting this. Might be due to a zombie.",
     "BRAILLE LINE:  '< > I am a hidden label!   Check me! check box image'",
     "     VISIBLE:  '< > I am a hidden label!   Check', cursor=1",
     "SPEECH OUTPUT: 'I am a hidden label!   Check me! check box not checked'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["KNOWN ISSUE: We're displaying part of the hidden label",
     "BRAILLE LINE:  'I '",
     "     VISIBLE:  'I ', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'End'",
     "     VISIBLE:  'End', cursor=1",
     "SPEECH OUTPUT: 'End'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["KNOWN ISSUE: We're displaying the hidden label",
     "BRAILLE LINE:  'I am a hidden label!   Check me!'",
     "     VISIBLE:  'I am a hidden label!   Check me!', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  '< > I am a hidden label!   Check me! check box image'",
     "     VISIBLE:  '< > I am a hidden label!   Check', cursor=1",
     "SPEECH OUTPUT: 'I am a hidden label!   Check me! check box not checked'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
