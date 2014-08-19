#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Table test foo bar table row foo foo bar bar table row Hello'",
     "SPEECH OUTPUT: 'heading level 3'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'This is a test'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' that is not very interesting. \u2022'",
     "SPEECH OUTPUT: 'But it looks like'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' a real-world example. \u2022'",
     "SPEECH OUTPUT: 'And that's'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' why this silly test is here. So it's '",
     "SPEECH OUTPUT: 'far more interesting'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' than it looks. World'",
     "SPEECH OUTPUT: 'heading level 3'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'The thing is'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' we can't copy content. •'",
     "SPEECH OUTPUT: 'So we must'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' create silly tests. •'",
     "SPEECH OUTPUT: 'Oh'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' well. At least it's '",
     "SPEECH OUTPUT: 'over'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
