#!/usr/bin/python

"""Test of flat review by word and char in a simple text document."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "1. Flat review current word",
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=1",
     "SPEECH OUTPUT: 'On '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "2. Flat review next word",
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "3. Spell current word",
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'p'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'colon'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "4. Spell current word phonetically",
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'p'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'colon'",
     "SPEECH OUTPUT: 'whiskey'",
     "SPEECH OUTPUT: 'echo'",
     "SPEECH OUTPUT: 'alpha'",
     "SPEECH OUTPUT: 'papa'",
     "SPEECH OUTPUT: 'oscar'",
     "SPEECH OUTPUT: 'november'",
     "SPEECH OUTPUT: 'romeo'",
     "SPEECH OUTPUT: 'yankee'",
     "SPEECH OUTPUT: ':'"]))

sequence.append(KeyComboAction("KP_6"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "5. flat review next word",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "6. flat review next word",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "SPEECH OUTPUT: 'expects '"]))

sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "7. flat review current char",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "SPEECH OUTPUT: 'expects '",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "8. phonetic for current char",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'echo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "9. unicode for current char",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'echo'",
     "SPEECH OUTPUT: 'Unicode 0065'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "10. flat review next char",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=9",
     "SPEECH OUTPUT: 'x'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "11. flat review next char",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=10",
     "SPEECH OUTPUT: 'p'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "12. flat review previous char",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=9",
     "SPEECH OUTPUT: 'x'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "13. flat review previous char",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "14. flat review previous word",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY '"]))

sequence.append(KeyComboAction("KP_4"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "15. flat review previous word",
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
