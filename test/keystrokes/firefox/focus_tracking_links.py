#!/usr/bin/python

"""Test of the fix for bug 511389."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Hello world, this is a test.'",
     "     VISIBLE:  'Hello world, this is a test.', cursor=1",
     "SPEECH OUTPUT: 'Hello world'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ', this is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down to the Foo link",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to the Bar link",
    ["BRAILLE LINE:  'Bar'",
     "     VISIBLE:  'Bar', cursor=1",
     "SPEECH OUTPUT: 'Bar link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Shift Tab back to the Foo link",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo link.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
