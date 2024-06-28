#!/usr/bin/python

"""Test of menu bar output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Right Arrow on menu bar",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Edit menu'",
     "     VISIBLE:  'Edit menu', cursor=1",
     "BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar Undo grayed\\(Ctrl\\+Z\\)'",
     "     VISIBLE:  'Undo grayed(Ctrl+Z)', cursor=1",
     "SPEECH OUTPUT: 'Edit menu.'",
     "SPEECH OUTPUT: 'Undo grayed Ctrl+Z.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Left Arrow on menu bar",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar File menu'",
     "     VISIBLE:  'File menu', cursor=1",
     "BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar New Tab\\(Ctrl\\+T\\)'",
     "     VISIBLE:  'New Tab(Ctrl+T)', cursor=1",
     "SPEECH OUTPUT: 'File menu.'",
     "SPEECH OUTPUT: 'New Tab Ctrl+T.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar New Tab\\(Ctrl\\+T\\)'",
     "     VISIBLE:  'New Tab(Ctrl+T)', cursor=1",
     "SPEECH OUTPUT: 'File menu'",
     "SPEECH OUTPUT: 'Menu Bar tool bar.'",
     "SPEECH OUTPUT: 'New Tab.'",
     "SPEECH OUTPUT: 'Ctrl+T.'",
     "SPEECH OUTPUT: '1 of 13.'",
     "SPEECH OUTPUT: 'T'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
