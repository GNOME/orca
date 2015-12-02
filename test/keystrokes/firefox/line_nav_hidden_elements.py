#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This element is not hidden.'",
     "     VISIBLE:  'This element is not hidden.', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'This element hidden by position off screen.'",
     "     VISIBLE:  'This element hidden by position ', cursor=1",
     "SPEECH OUTPUT: 'This element hidden by position off screen.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'This element is in a parent which is not hidden.'",
     "     VISIBLE:  'This element is in a parent whic', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent which is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'This element is in a parent hidden by position off screen'",
     "     VISIBLE:  'This element is in a parent hidd', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent hidden by position off screen'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'This element is not hidden.'",
     "     VISIBLE:  'This element is not hidden.', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'This element is in a parent hidden by position off screen'",
     "     VISIBLE:  'This element is in a parent hidd', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent hidden by position off screen'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'This element is in a parent which is not hidden.'",
     "     VISIBLE:  'This element is in a parent whic', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent which is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'This element hidden by position off screen.'",
     "     VISIBLE:  'This element hidden by position ', cursor=1",
     "SPEECH OUTPUT: 'This element hidden by position off screen.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'This element is not hidden.'",
     "     VISIBLE:  'This element is not hidden.', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
