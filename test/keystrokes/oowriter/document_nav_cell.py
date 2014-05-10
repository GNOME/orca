#!/usr/bin/python

"""Test of speech output when tabbing amongst table cells."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to Tue",
    ["BRAILLE LINE:  'Tue $l'",
     "     VISIBLE:  'Tue $l', cursor=1",
     "SPEECH OUTPUT: 'Tue'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to Wed",
    ["BRAILLE LINE:  'Wed $l'",
     "     VISIBLE:  'Wed $l', cursor=1",
     "SPEECH OUTPUT: 'Wed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to Thu",
    ["BRAILLE LINE:  'Thu $l'",
     "     VISIBLE:  'Thu $l', cursor=1",
     "SPEECH OUTPUT: 'Thu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to Fri",
    ["BRAILLE LINE:  'Fri $l'",
     "     VISIBLE:  'Fri $l', cursor=1",
     "SPEECH OUTPUT: 'Fri'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to Sat",
    ["BRAILLE LINE:  'Sat $l'",
     "     VISIBLE:  'Sat $l', cursor=1",
     "SPEECH OUTPUT: 'Sat'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to blank cell in next row",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank blank blank blank blank 1 2'"]))

sequence.append(KeyComboAction("<Control>w"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
