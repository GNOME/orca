#!/usr/bin/python

"""Test WhereAmI presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Basic WhereAmI with no text selected",
    ["SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and '"]))

sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic WhereAmI with multiple paragraphs selected",
    ["SPEECH OUTPUT: 'Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn! Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. Hm! She is made  selected'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
