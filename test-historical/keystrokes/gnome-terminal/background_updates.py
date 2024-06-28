#!/usr/bin/python

from macaroon.playback import *
import utils

utils.setClipboardText('for i in {0..50}; do echo "Count: $i"; sleep 2;  done')

sequence = MacroSequence()
sequence.append(KeyComboAction("<Control><Shift>v"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("<Control><Shift>t"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))
sequence.append(utils.AssertPresentationAction(
    "1. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))
sequence.append(utils.AssertPresentationAction(
    "2. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))
sequence.append(utils.AssertPresentationAction(
    "3. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(KeyComboAction("<Control><Shift>n"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))
sequence.append(utils.AssertPresentationAction(
    "4. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))
sequence.append(utils.AssertPresentationAction(
    "5. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))
sequence.append(utils.AssertPresentationAction(
    "6. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
