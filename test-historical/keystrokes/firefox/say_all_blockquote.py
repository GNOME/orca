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
    ["SPEECH OUTPUT: 'On weaponry:'",
     "SPEECH OUTPUT: 'block quote'",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition!'",
     "SPEECH OUTPUT: 'Our chief weapon is surprise.'",
     "SPEECH OUTPUT: 'Surprise and fear.'",
     "SPEECH OUTPUT: 'Fear and surprise.'",
     "SPEECH OUTPUT: 'Our two weapons are fear and surprise.'",
     "SPEECH OUTPUT: 'And ruthless efficiency.'",
     "SPEECH OUTPUT: 'Our three weapons are fear, surprise, and ruthless efficiency.'",
     "SPEECH OUTPUT: 'And an almost fanatical devotion to the Pope.'",
     "SPEECH OUTPUT: 'Our four.'",
     "SPEECH OUTPUT: 'No.'",
     "SPEECH OUTPUT: 'Amongst our weapons.'",
     "SPEECH OUTPUT: 'Amongst our weaponry, are such elements as fear, surprise.'",
     "SPEECH OUTPUT: 'I'll come in again.'",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition!'",
     "SPEECH OUTPUT: 'Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'On old ladies:'",
     "SPEECH OUTPUT: 'block quote'",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance.'",
     "SPEECH OUTPUT: 'Confess the heinous sin of heresy, reject the works of the ungodly.'",
     "SPEECH OUTPUT: 'Two last chances.'",
     "SPEECH OUTPUT: 'And you shall be free.'",
     "SPEECH OUTPUT: 'Three last chances.'",
     "SPEECH OUTPUT: 'You have three last chances, the nature of which I have divulged in my previous utterance.'",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'On castle decor:'",
     "SPEECH OUTPUT: 'block quote'",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff!'",
     "SPEECH OUTPUT: 'Cardinal Fang!'",
     "SPEECH OUTPUT: 'Fetch the COMFY CHAIR!'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
