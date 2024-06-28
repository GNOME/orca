#!/usr/bin/python

"""Test of structural navigation by blockquote."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "1. q to first quote", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "2. q to second quote", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "3. q to third quote", 
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "4. q wrap to top", 
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift+q wrap to bottom", 
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(utils.AssertPresentationAction(
    "6. Shift+q to second quote", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. Basic Where Am I",
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the '",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
