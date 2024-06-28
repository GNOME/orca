#!/usr/bin/python

"""Test of Dojo tab container presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to tab list",
    ["BRAILLE LINE:  'Tab 2 page tab'",
     "     VISIBLE:  'Tab 2 page tab', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Tab 2 page tab.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right arrow to next tab",
    ["BRAILLE LINE:  'Tab 2 page tab'",
     "     VISIBLE:  'Tab 2 page tab', cursor=1",
     "BRAILLE LINE:  'Tab 3 page tab'",
     "     VISIBLE:  'Tab 3 page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab 3 page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right arrow to next tab",
    ["BRAILLE LINE:  'Inlined Sub TabContainer page tab'",
     "     VISIBLE:  'Inlined Sub TabContainer page ta', cursor=1",
     "SPEECH OUTPUT: 'Inlined Sub TabContainer page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to contents",
    ["BRAILLE LINE:  'SubTab 2 page tab'",
     "     VISIBLE:  'SubTab 2 page tab', cursor=1",
     "SPEECH OUTPUT: 'SubTab 2 page tab.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
