#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("g"))
sequence.append(utils.AssertPresentationAction(
    "1. Use g to navigate to the image",
    ["BRAILLE LINE:  'the image image'",
     "     VISIBLE:  'the image image', cursor=1",
     "SPEECH OUTPUT: 'the image'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'has long description'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I on image",
    ["BRAILLE LINE:  'the image image'",
     "     VISIBLE:  'the image image', cursor=1",
     "SPEECH OUTPUT: 'the image'",
     "SPEECH OUTPUT: 'image has long description'"]))

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("KP_Multiply"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("d"))
sequence.append(WaitForDocLoad())

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Having selected View Description, do a Where Am I for new location",
    ["KNOWN ISSUE: Braille and eyeballs suggest we're in the right place. Speech does not. The test case states the image is broken.",
     "BRAILLE LINE:  'Pass h1'",
     "     VISIBLE:  'Pass h1', cursor=1",
     "SPEECH OUTPUT: 'the image'",
     "SPEECH OUTPUT: 'invalid'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
