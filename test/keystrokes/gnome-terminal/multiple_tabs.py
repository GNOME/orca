#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("ftp"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Return",
    ["BRAILLE LINE:  'ftp> '",
     "     VISIBLE:  'ftp> ', cursor=6",
     "SPEECH OUTPUT: 'ftp> '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Return",
    ["BRAILLE LINE:  'ftp> '",
     "     VISIBLE:  'ftp> ', cursor=6",
     "SPEECH OUTPUT: 'ftp> '"]))

sequence.append(KeyComboAction("<Control><Shift>t"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "4. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(KeyComboAction("<Alt>1"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "5. Return",
    ["BRAILLE LINE:  'ftp> '",
     "     VISIBLE:  'ftp> ', cursor=6",
     "SPEECH OUTPUT: 'ftp> '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "6. Return",
    ["BRAILLE LINE:  'ftp> '",
     "     VISIBLE:  'ftp> ', cursor=6",
     "SPEECH OUTPUT: 'ftp> '"]))

sequence.append(KeyComboAction("<Alt>2"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "7. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "8. Return",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: '$ '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
