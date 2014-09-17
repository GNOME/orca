#!/usr/bin/python

"""Test of navigation by Home/End on a blank line."""

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("Right"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "1. End",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'newline'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "2. Home",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'newline'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
