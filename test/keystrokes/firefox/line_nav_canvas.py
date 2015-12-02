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
    ["BRAILLE LINE:  'line 1'",
     "     VISIBLE:  'line 1', cursor=1",
     "SPEECH OUTPUT: 'line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'line 2 canvas'",
     "     VISIBLE:  'line 2 canvas', cursor=1",
     "SPEECH OUTPUT: 'line 2 canvas.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'line 3'",
     "     VISIBLE:  'line 3', cursor=1",
     "SPEECH OUTPUT: 'line 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'line  4'",
     "     VISIBLE:  'line  4', cursor=1",
     "SPEECH OUTPUT: 'line'",
     "SPEECH OUTPUT: '4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'line 5 canvas'",
     "     VISIBLE:  'line 5 canvas', cursor=1",
     "SPEECH OUTPUT: 'line 5 canvas.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
