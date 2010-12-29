# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of flat review by line in a simple text document."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local blockquote test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "blockquotes.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Blockquote Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(3000))

########################################################################
# Read the current line with KP_8.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8", 1000))
sequence.append(utils.AssertPresentationAction(
    "flat review current line", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=1",
     "SPEECH OUTPUT: 'On weaponry:'"]))

########################################################################
# Read the rest of the document with KP_9.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope.  $l'",
     "     VISIBLE:  'surprise. And ruthless efficienc', cursor=1",
     "SPEECH OUTPUT: 'surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the  $l'",
     "     VISIBLE:  'Our four. No. Amongst our weapon', cursor=1",
     "SPEECH OUTPUT: 'Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the  $l'",
     "     VISIBLE:  'Spanish Inquisition! Amongst our', cursor=1",
     "SPEECH OUTPUT: 'Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BUG? - Why are we presenting the text twice?",
     "BRAILLE LINE:  'Pope, and nice red uniforms - Oh damn! Pope, and nice red uniforms - Oh damn!  $l'",
     "     VISIBLE:  'Pope, and nice red uniforms - Oh', cursor=1",
     "SPEECH OUTPUT: 'Pope, and nice red uniforms - Oh damn! Pope, and nice red uniforms - Oh damn! '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'On old ladies: $l'",
     "     VISIBLE:  'On old ladies: $l', cursor=1",
     "SPEECH OUTPUT: 'On old ladies:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall  $l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BUG? - Why are we presenting the text twice?",
     "BRAILLE LINE:  'be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.  $l'",
     "     VISIBLE:  'be free. Three last chances. You', cursor=1",
     "SPEECH OUTPUT: 'be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'On castle decor: $l'",
     "     VISIBLE:  'On castle decor: $l', cursor=1",
     "SPEECH OUTPUT: 'On castle decor:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!  $l'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! '"]))

########################################################################
# Read the document in reverse order with KP_7.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'On castle decor: $l'",
     "     VISIBLE:  'On castle decor: $l', cursor=1",
     "SPEECH OUTPUT: 'On castle decor:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BUG? - Why are we presenting the text twice?",
     "BRAILLE LINE:  'be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.  $l'",
     "     VISIBLE:  'be free. Three last chances. You', cursor=1",
     "SPEECH OUTPUT: 'be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall  $l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'On old ladies: $l'",
     "     VISIBLE:  'On old ladies: $l', cursor=1",
     "SPEECH OUTPUT: 'On old ladies:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BUG? - Why are we presenting the text twice?",
     "BRAILLE LINE:  'Pope, and nice red uniforms - Oh damn! Pope, and nice red uniforms - Oh damn!  $l'",
     "     VISIBLE:  'Pope, and nice red uniforms - Oh', cursor=1",
     "SPEECH OUTPUT: 'Pope, and nice red uniforms - Oh damn! Pope, and nice red uniforms - Oh damn! '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the  $l'",
     "     VISIBLE:  'Spanish Inquisition! Amongst our', cursor=1",
     "SPEECH OUTPUT: 'Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the  $l'",
     "     VISIBLE:  'Our four. No. Amongst our weapon', cursor=1",
     "SPEECH OUTPUT: 'Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope.  $l'",
     "     VISIBLE:  'surprise. And ruthless efficienc', cursor=1",
     "SPEECH OUTPUT: 'surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=1",
     "SPEECH OUTPUT: 'On weaponry:'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
