#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Where Am I on image",
    ["BRAILLE LINE:  'the image image'",
     "     VISIBLE:  'the image image', cursor=(0|1)",
     "SPEECH OUTPUT: 'the image image has long description'"]))

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("KP_Multiply"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("d"))
#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Having selected View Description, do a Where Am I for new location",
    ["BRAILLE LINE:  'Pass h1'",
     "     VISIBLE:  'Pass h1', cursor=1",
     "SPEECH OUTPUT: 'heading level 1.'",
     "SPEECH OUTPUT: 'Pass'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
