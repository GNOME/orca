#!/usr/bin/python

"""Test flat review by line."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Return"))

sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line.",
    ["BRAILLE LINE:  'Line 1 $l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "2. Review next line.",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "3. Spell current line.",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'L'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "4. Phonetic spell current line.",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'L'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: '2'",
     "SPEECH OUTPUT: 'lima'",
     "SPEECH OUTPUT: 'india'",
     "SPEECH OUTPUT: 'november'",
     "SPEECH OUTPUT: 'echo'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous line.",
    ["BRAILLE LINE:  'Line 1 $l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
