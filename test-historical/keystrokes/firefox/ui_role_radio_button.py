#!/usr/bin/python

"""Test of radio button output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(KeyComboAction("p"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>a"))
sequence.append(utils.AssertPresentationAction(
    "1. Alt a to radio button group",
    ["BRAILLE LINE:  'Firefox application Print dialog General page tab Range Range &=y All Pages radio button'",
     "     VISIBLE:  '&=y All Pages radio button', cursor=1",
     "SPEECH OUTPUT: 'Range panel.'",
     "SPEECH OUTPUT: 'All Pages.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Print dialog General page tab Range Range &=y All Pages radio button'",
     "     VISIBLE:  '&=y All Pages radio button', cursor=1",
     "SPEECH OUTPUT: 'Range.'",
     "SPEECH OUTPUT: 'All Pages radio button.'",
     "SPEECH OUTPUT: 'selected.'",
     "SPEECH OUTPUT: '1 of 4.'",
     "SPEECH OUTPUT: 'Alt+A'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
