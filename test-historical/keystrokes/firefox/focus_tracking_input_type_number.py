#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab",
    ["BRAILLE LINE:  '0 $l'",
     "     VISIBLE:  '0 $l', cursor=2",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'entry 0 selected.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  '0 $l'",
     "     VISIBLE:  '0 $l', cursor=2",
     "BRAILLE LINE:  '-1 $l'",
     "     VISIBLE:  '-1 $l', cursor=3",
     "BRAILLE LINE:  '-1 $l'",
     "     VISIBLE:  '-1 $l', cursor=3",
     "SPEECH OUTPUT: '-1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down",
    ["BRAILLE LINE:  '-2 $l'",
     "     VISIBLE:  '-2 $l', cursor=3",
     "BRAILLE LINE:  '-2 $l'",
     "     VISIBLE:  '-2 $l', cursor=3",
     "SPEECH OUTPUT: '-2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up",
    ["BRAILLE LINE:  '-1 $l'",
     "     VISIBLE:  '-1 $l', cursor=3",
     "BRAILLE LINE:  '-1 $l'",
     "     VISIBLE:  '-1 $l', cursor=3",
     "SPEECH OUTPUT: '-1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
