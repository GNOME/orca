#!/usr/bin/python

"""Test of menu checkbox output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>v"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow in View menu",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar < > Full Screen check menu item'",
     "     VISIBLE:  '< > Full Screen check menu item', cursor=1",
     "SPEECH OUTPUT: 'Full Screen check menu item not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar < > Full Screen check menu item'",
     "     VISIBLE:  '< > Full Screen check menu item', cursor=1",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Menu Bar tool bar.'",
     "SPEECH OUTPUT: 'Full Screen check menu item not checked.'",
     "SPEECH OUTPUT: '6 of 6.'",
     "SPEECH OUTPUT: 'F'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
