#!/usr/bin/python

"""Test of tree table output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>b"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow in tree table",
    ["BRAILLE LINE:  'Firefox application Library frame tree table Bookmarks Menu   table row TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Menu   table row TREE ', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Menu   table row'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Library frame tree table Bookmarks Menu   table row TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Menu   table row TREE ', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Menu   table row'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow in tree table",
    ["BRAILLE LINE:  'Firefox application Library frame tree table Bookmarks Toolbar   table row TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Toolbar   table row TR', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Toolbar   table row'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
