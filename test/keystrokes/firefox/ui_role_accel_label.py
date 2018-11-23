#!/usr/bin/python

"""Test of menu accelerator label output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(2000))
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow in File menu",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar New Window\\(Ctrl\\+N\\)'",
     "     VISIBLE:  'New Window(Ctrl+N)', cursor=1",
     "SPEECH OUTPUT: 'New Window Ctrl+N.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow in File menu",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar New Private Window\\(Shift\\+Ctrl\\+P\\)'",
     "     VISIBLE:  'New Private Window(Shift+Ctrl+P)', cursor=1",
     "SPEECH OUTPUT: 'New Private Window Shift+Ctrl+P.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar New Private Window\\(Shift\\+Ctrl\\+P\\)'",
     "     VISIBLE:  'New Private Window(Shift+Ctrl+P)', cursor=1",
     "SPEECH OUTPUT: 'File menu'",
     "SPEECH OUTPUT: 'Menu Bar tool bar.'",
     "SPEECH OUTPUT: 'New Private Window.'",
     "SPEECH OUTPUT: 'Shift+Ctrl+P.'",
     "SPEECH OUTPUT: '4 of 13.'",
     "SPEECH OUTPUT: 'W'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
