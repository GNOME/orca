# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of flat review by line in a simple text document."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local blockquote test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

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
sequence.append(KeyComboAction("KP_8"))
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
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear,  $l'",
     "     VISIBLE:  'surprise. Our two weapons are fe', cursor=1",
     "SPEECH OUTPUT: 'surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst  $l'",
     "     VISIBLE:  'surprise, and ruthless efficienc', cursor=1",
     "SPEECH OUTPUT: 'surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY  $l'",
     "     VISIBLE:  'our weapons. Amongst our weaponr', cursor=1",
     "SPEECH OUTPUT: 'our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise,  $l'",
     "     VISIBLE:  'expects the Spanish Inquisition!', cursor=1",
     "SPEECH OUTPUT: 'expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!  $l'",
     "     VISIBLE:  'ruthless efficiency, an almost f', cursor=1",
     "SPEECH OUTPUT: 'ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn! '"]))

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
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the  $l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the  $l'",
     "     VISIBLE:  'ungodly. Two last chances. And y', cursor=1",
     "SPEECH OUTPUT: 'ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'nature of which I have divulged in my previous utterance.  $l'",
     "     VISIBLE:  'nature of which I have divulged ', cursor=1",
     "SPEECH OUTPUT: 'nature of which I have divulged in my previous utterance. '"]))

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
    ["BRAILLE LINE:  'nature of which I have divulged in my previous utterance.  $l'",
     "     VISIBLE:  'nature of which I have divulged ', cursor=1",
     "SPEECH OUTPUT: 'nature of which I have divulged in my previous utterance. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the  $l'",
     "     VISIBLE:  'ungodly. Two last chances. And y', cursor=1",
     "SPEECH OUTPUT: 'ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the  $l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the '"]))

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
    ["BRAILLE LINE:  'ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!  $l'",
     "     VISIBLE:  'ruthless efficiency, an almost f', cursor=1",
     "SPEECH OUTPUT: 'ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn! '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise,  $l'",
     "     VISIBLE:  'expects the Spanish Inquisition!', cursor=1",
     "SPEECH OUTPUT: 'expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY  $l'",
     "     VISIBLE:  'our weapons. Amongst our weaponr', cursor=1",
     "SPEECH OUTPUT: 'our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst  $l'",
     "     VISIBLE:  'surprise, and ruthless efficienc', cursor=1",
     "SPEECH OUTPUT: 'surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear,  $l'",
     "     VISIBLE:  'surprise. Our two weapons are fe', cursor=1",
     "SPEECH OUTPUT: 'surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous line", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and '"]))

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
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
