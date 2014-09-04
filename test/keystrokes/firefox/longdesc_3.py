#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Where Am I on image",
    ["BRAILLE LINE:  'the image image'",
     "     VISIBLE:  'the image image', cursor=0",
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
    "2. Having selected View Description, do a Where Am I for new location",
    ["KNOWN ISSUE: This test fails not because of longdesc, but because jumping to any anchor in a page is broken",
     "BRAILLE LINE:  'Fail if you land here h1'",
     "     VISIBLE:  'Fail if you land here h1', cursor=1",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'Fail if you land here'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
