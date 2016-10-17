#!/usr/bin/python

"""Test of presentation of caret navigation by paragraph."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Next paragraph",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Next paragraph",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Next paragraph",
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject  $l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Next paragraph",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Next paragraph",
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! $l'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Previous paragraph",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Previous paragraph",
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject  $l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Previous paragraph",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Previous paragraph",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
