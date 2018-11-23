#!/usr/bin/python

"""Test of tree table output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>b"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow in tree table",
    ["BRAILLE LINE:  'Firefox application Library frame tree table Mozilla   table row TREE LEVEL 1'",
     "     VISIBLE:  'Mozilla   table row TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: 'Mozilla  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Library frame tree table Mozilla   table row TREE LEVEL 1'",
     "     VISIBLE:  'Mozilla   table row TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: 'Mozilla   table row.'",
     "SPEECH OUTPUT: '2 of 3.'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow in tree table",
    ["BRAILLE LINE:  'Firefox application Library frame tree table GNOME   table row TREE LEVEL 1'",
     "     VISIBLE:  'GNOME   table row TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: 'GNOME  '"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
