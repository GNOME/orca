#!/usr/bin/python

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
    ["BRAILLE LINE:  'math Line 2'",
     "     VISIBLE:  'math Line 2', cursor=0",
     "SPEECH OUTPUT: '1 plus 1 equals'",
     "SPEECH OUTPUT: 'Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '2+2=Line 4'",
     "     VISIBLE:  '2+2=Line 4', cursor=1",
     "SPEECH OUTPUT: '2+2='",
     "SPEECH OUTPUT: 'Line 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Line 5'",
     "     VISIBLE:  'Line 5', cursor=1",
     "SPEECH OUTPUT: 'Line 5'"]))

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
    ["BRAILLE LINE:  'math math Line 7'",
     "     VISIBLE:  'math math Line 7', cursor=0",
     "SPEECH OUTPUT: '3 plus 4 equals'",
     "SPEECH OUTPUT: '5 plus 2 equals'",
     "SPEECH OUTPUT: 'Line 7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'Line 8'",
     "     VISIBLE:  'Line 8', cursor=1",
     "SPEECH OUTPUT: 'Line 8'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'math math Line 7'",
     "     VISIBLE:  'math math Line 7', cursor=0",
     "SPEECH OUTPUT: '3 plus 4 equals'",
     "SPEECH OUTPUT: '5 plus 2 equals'",
     "SPEECH OUTPUT: 'Line 7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'Line 6'",
     "     VISIBLE:  'Line 6', cursor=1",
     "SPEECH OUTPUT: 'Line 6'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'Line 5'",
     "     VISIBLE:  'Line 5', cursor=1",
     "SPEECH OUTPUT: 'Line 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  '2+2=Line 4'",
     "     VISIBLE:  '2+2=Line 4', cursor=1",
     "SPEECH OUTPUT: '2+2='",
     "SPEECH OUTPUT: 'Line 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'math Line 2'",
     "     VISIBLE:  'math Line 2', cursor=0",
     "SPEECH OUTPUT: '1 plus 1 equals'",
     "SPEECH OUTPUT: 'Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
