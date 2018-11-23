#!/usr/bin/python

"""Test of flat review by line in a simple text document."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Flat review current line",
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=1",
     "SPEECH OUTPUT: 'On weaponry:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "2. Flat review next line",
    ["BRAILLE LINE:  'block quote $l'",
     "     VISIBLE:  'block quote $l', cursor=1",
     "SPEECH OUTPUT: 'block quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "3. Flat review next line",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Flat review next line",
    ["BRAILLE LINE:  'surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear,  $l'",
     "     VISIBLE:  'surprise. Our two weapons are fe', cursor=1",
     "SPEECH OUTPUT: 'surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Flat review previous line",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "6. Flat review previous line",
    ["BRAILLE LINE:  'block quote $l'",
     "     VISIBLE:  'block quote $l', cursor=1",
     "SPEECH OUTPUT: 'block quote'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
