#!/usr/bin/python

"""Test of flat review in content with hidden elements."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Flat review current line",
    ["BRAILLE LINE:  'This element is not hidden. $l'",
     "     VISIBLE:  'This element is not hidden. $l', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "2. Flat review next line",
    ["BRAILLE LINE:  'This element is in a parent which is not hidden. $l'",
     "     VISIBLE:  'This element is in a parent whic', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent which is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "3. Flat review next line",
    ["BRAILLE LINE:  'This element is not hidden. $l'",
     "     VISIBLE:  'This element is not hidden. $l', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "4. Flat review previous line",
    ["BRAILLE LINE:  'This element is in a parent which is not hidden. $l'",
     "     VISIBLE:  'This element is in a parent whic', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent which is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Flat review previous line",
    ["BRAILLE LINE:  'This element is not hidden. $l'",
     "     VISIBLE:  'This element is not hidden. $l', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
