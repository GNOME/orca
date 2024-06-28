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
    ["BRAILLE LINE:  'Guess me 1:  $l'",
     "     VISIBLE:  'Guess me 1:  $l', cursor=13",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Guess me 1: entry.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'Guess me 1:  $l'",
     "     VISIBLE:  'Guess me 1:  $l', cursor=13",
     "BRAILLE LINE:  'E-mail:  $l'",
     "     VISIBLE:  'E-mail:  $l', cursor=9",
     "SPEECH OUTPUT: 'E-mail: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'Secret:  $l'",
     "     VISIBLE:  'Secret:  $l', cursor=9",
     "SPEECH OUTPUT: 'Secret: password text'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
