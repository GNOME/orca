#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(3000))
sequence.append(TypeAction("foo"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Return after typing 'foo'",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'bash: foo: command not found...'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
