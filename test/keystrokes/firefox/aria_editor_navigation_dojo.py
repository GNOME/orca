#!/usr/bin/python

"""Test navigation out of the Dojo editor."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow in Focus Mode",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("a"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Toggle Browse Mode",
    ["BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow in Browse Mode",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "BRAILLE LINE:  'editor0 tool bar'",
     "     VISIBLE:  'editor0 tool bar', cursor=1",
     "SPEECH OUTPUT: 'editor0'",
     "SPEECH OUTPUT: 'tool bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow in Browse Mode",
    ["BRAILLE LINE:  'No plugins, initially empty h2'",
     "     VISIBLE:  'No plugins, initially empty h2', cursor=1",
     "SPEECH OUTPUT: 'No plugins, initially empty'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
