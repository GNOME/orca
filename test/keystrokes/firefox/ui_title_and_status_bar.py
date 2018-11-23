#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Title bar",
    ["BRAILLE LINE:  'Links to test files - Firefox Nightly'",
     "     VISIBLE:  'Links to test files - Firefox Ni', cursor=0",
     "SPEECH OUTPUT: 'Links to test files - Firefox Nightly'"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Status bar",
    ["BRAILLE LINE:  'Links to test files - Firefox Nightly'",
     "     VISIBLE:  'Links to test files - Firefox Ni', cursor=0",
     "BRAILLE LINE:  'anchors.html'",
     "     VISIBLE:  'anchors.html', cursor=1",
     "BRAILLE LINE:  'anchors.html'",
     "     VISIBLE:  'anchors.html', cursor=1",
     "SPEECH OUTPUT: 'Links to test files - Firefox Nightly'",
     "SPEECH OUTPUT: 'file:///.+/anchors.html'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
