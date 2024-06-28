#!/usr/bin/python

from macaroon.playback import *
import utils

utils.setClipboardText('PS1="prompt> "')

sequence = MacroSequence()

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Return in old shell",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(TypeAction("bash"))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.StartRecordingAction())

sequence.append(KeyComboAction("<Control><Shift>v"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Return in new shell with changed prompt",
    ["BRAILLE LINE:  'prompt> '",
     "     VISIBLE:  'prompt> ', cursor=9",
     "SPEECH OUTPUT: 'prompt> '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>d"))
sequence.append(utils.AssertPresentationAction(
    "3. Ctrl+D to exit new shell",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: 'prompt> exit",
     "$ '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "4. Return in old shell",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
