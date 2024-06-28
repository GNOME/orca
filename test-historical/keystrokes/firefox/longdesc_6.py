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
    ["KNOWN ISSUE: 'Empty images are exposed to us as text, without AtspiAction, and the Firefox right-click menu lacks View Description",
     "BRAILLE LINE:  'the image'",
     "     VISIBLE:  'the image', cursor=1",
     "SPEECH OUTPUT: 'the image'"]))

#sequence.append(PauseAction(3000))
#sequence.append(KeyComboAction("KP_Multiply"))
#sequence.append(PauseAction(3000))
#sequence.append(KeyComboAction("d"))
##sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("KP_Enter"))
#sequence.append(utils.AssertPresentationAction(
#    "2. Having selected View Description, do a Where Am I for new location", 
#    ["BRAILLE LINE:  'Pass h1'",
#     "     VISIBLE:  'Pass h1', cursor=1",
#     "SPEECH OUTPUT: 'heading level 1'",
#     "SPEECH OUTPUT: 'Pass'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
