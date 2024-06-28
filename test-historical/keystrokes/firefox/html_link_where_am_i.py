#!/usr/bin/python

"""Test of Where am I for links."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Shift>Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Title bar",
    ["BRAILLE LINE:  'Product summary'",
     "     VISIBLE:  'Product summary', cursor=1",
     "BRAILLE LINE:  'GNOME Bug Tracking System - Firefox Nightly'",
     "     VISIBLE:  'GNOME Bug Tracking System - Fire', cursor=0",
     "SPEECH OUTPUT: 'GNOME Bug Tracking System - Firefox Nightly'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I on Product summary link", 
    ["BRAILLE LINE:  'Product summary'",
     "     VISIBLE:  'Product summary', cursor=1",
     "BRAILLE LINE:  'Product summary'",
     "     VISIBLE:  'Product summary', cursor=1",
     "SPEECH OUTPUT: 'http link Product summary.'",
     "SPEECH OUTPUT: 'different site.'"]))

sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Title bar",
    ["BRAILLE LINE:  'GNOME Bug Tracking System - Firefox Nightly'",
     "     VISIBLE:  'GNOME Bug Tracking System - Fire', cursor=0",
     "SPEECH OUTPUT: 'GNOME Bug Tracking System - Firefox Nightly'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Where Am I on what should be the New bug link",
    ["BRAILLE LINE:  'New bug'",
     "     VISIBLE:  'New bug', cursor=1",
     "BRAILLE LINE:  'New bug'",
     "     VISIBLE:  'New bug', cursor=1",
     "SPEECH OUTPUT: 'http link New bug.'",
     "SPEECH OUTPUT: 'different site.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
