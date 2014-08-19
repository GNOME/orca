#!/usr/bin/python

"""Test of list item output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Alt>e"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Right Arrow in list",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Tabs list box General'",
     "     VISIBLE:  'General', cursor=1",
     "BRAILLE LINE:  'Firefox application Firefox Preferences dialog Tabs list box Tabs'",
     "     VISIBLE:  'Tabs', cursor=1",
     "SPEECH OUTPUT: 'Tabs'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Left Arrow in list",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog General list box Tabs'",
     "     VISIBLE:  'Tabs', cursor=1",
     "BRAILLE LINE:  'Firefox application Firefox Preferences dialog General list box General'",
     "     VISIBLE:  'General', cursor=1",
     "SPEECH OUTPUT: 'General'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog General list box General'",
     "     VISIBLE:  'General', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'General'",
     "SPEECH OUTPUT: '1 of 8'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
