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
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Line 2'",
     "     VISIBLE:  'Line 2', cursor=1",
     "SPEECH OUTPUT: 'foo region'",
     "SPEECH OUTPUT: 'Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Line 3 Close push button'",
     "     VISIBLE:  'Line 3 Close push button', cursor=1",
     "SPEECH OUTPUT: 'leaving region.'",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'Line 3 panel'",
     "SPEECH OUTPUT: 'Close push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Line 4'",
     "     VISIBLE:  'Line 4', cursor=1",
     "SPEECH OUTPUT: 'Line 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Line 5'",
     "     VISIBLE:  'Line 5', cursor=1",
     "SPEECH OUTPUT: 'leaving panel.'",
     "SPEECH OUTPUT: 'leaving form.'",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'Line 5 panel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Line 6'",
     "     VISIBLE:  'Line 6', cursor=1",
     "SPEECH OUTPUT: 'Line 6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Line 7'",
     "     VISIBLE:  'Line 7', cursor=1",
     "SPEECH OUTPUT: 'leaving panel.'",
     "SPEECH OUTPUT: 'leaving form.'",
     "SPEECH OUTPUT: 'Line 7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Line 6'",
     "     VISIBLE:  'Line 6', cursor=1",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'Line 5 panel'",
     "SPEECH OUTPUT: 'Line 6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'Line 5'",
     "     VISIBLE:  'Line 5', cursor=1",
     "SPEECH OUTPUT: 'Line 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'Line 4'",
     "     VISIBLE:  'Line 4', cursor=1",
     "SPEECH OUTPUT: 'leaving panel.'",
     "SPEECH OUTPUT: 'leaving form.'",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'Line 3 panel'",
     "SPEECH OUTPUT: 'Line 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'Line 3 Close push button'",
     "     VISIBLE:  'Line 3 Close push button', cursor=1",
     "SPEECH OUTPUT: 'Line 3'",
     "SPEECH OUTPUT: 'Close push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'Line 2'",
     "     VISIBLE:  'Line 2', cursor=1",
     "SPEECH OUTPUT: 'leaving panel.'",
     "SPEECH OUTPUT: 'leaving form.'",
     "SPEECH OUTPUT: 'foo region'",
     "SPEECH OUTPUT: 'Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'leaving region.'",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
