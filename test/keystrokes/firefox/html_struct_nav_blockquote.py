#!/usr/bin/python

"""Test of structural navigation by blockquote."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "1. q to first quote", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "2. q to second quote", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "3. q to third quote", 
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "4. q wrap to top", 
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift+q wrap to bottom", 
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! "]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(utils.AssertPresentationAction(
    "6. Shift+q wrap to second quote", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. Basic Where Am I",
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
