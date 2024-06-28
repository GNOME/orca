#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'FAQ'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'Battery'",
     "SPEECH OUTPUT: 'heading level 2'",
     "SPEECH OUTPUT: 'Q. What's a battery?'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Q. Which way is up?'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'FOO'",
     "SPEECH OUTPUT: 'heading level 2'",
     "SPEECH OUTPUT: 'Q. Why would someone put a line break in a heading?'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Q. What is the airspeed velocity of an unladen swallow?'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Battery'",
     "SPEECH OUTPUT: 'heading level 2'",
     "SPEECH OUTPUT: 'Q. What is a battery?",
     "SPEECH OUTPUT: 'A.'",
     "SPEECH OUTPUT: 'Look it up.'",
     "SPEECH OUTPUT: 'Q. Which way is up?",
     "SPEECH OUTPUT: 'A.'",
     "SPEECH OUTPUT: 'That way.'",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?",
     "SPEECH OUTPUT: 'A.'",
     "SPEECH OUTPUT: 'Empty anchors.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
