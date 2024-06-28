#!/usr/bin/python

"""Test of speech output when tabbing amongst table cells."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to Tue",
    ["BRAILLE LINE:  'Tue $l'",
     "     VISIBLE:  'Tue $l', cursor=1",
     "SPEECH OUTPUT: 'Tue C1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to Wed",
    ["BRAILLE LINE:  'Wed $l'",
     "     VISIBLE:  'Wed $l', cursor=1",
     "SPEECH OUTPUT: 'Wed D1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to Thu",
    ["BRAILLE LINE:  'Thu $l'",
     "     VISIBLE:  'Thu $l', cursor=1",
     "SPEECH OUTPUT: 'Thu E1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to Fri",
    ["BRAILLE LINE:  'Fri $l'",
     "     VISIBLE:  'Fri $l', cursor=1",
     "SPEECH OUTPUT: 'Fri F1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to Sat",
    ["BRAILLE LINE:  'Sat $l'",
     "     VISIBLE:  'Sat $l', cursor=1",
     "SPEECH OUTPUT: 'Sat G1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to blank cell in next row",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank A2.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
