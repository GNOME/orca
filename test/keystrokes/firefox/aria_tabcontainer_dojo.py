#!/usr/bin/python

"""Test of Dojo tab container presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to tab list",
    ["BRAILLE LINE:  '  push button  push button Tab 1 page tab Tab 2 page tab Tab 3 page tab Inlined Sub TabContainer page tab Sub TabContainer from href page tab SplitContainer from href page tab Embedded layout widgets page tab'",
     "     VISIBLE:  'Tab 2 page tab Tab 3 page tab In', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'Tab 2 page tab'",
     "     VISIBLE:  'Tab 2 page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab 2'",
     "SPEECH OUTPUT: 'page tab'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right arrow to next tab",
    ["BRAILLE LINE:  'Tab 3 page tab'",
     "     VISIBLE:  'Tab 3 page tab', cursor=1",
     "BRAILLE LINE:  'Tab 3 page tab'",
     "     VISIBLE:  'Tab 3 page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab 3'",
     "SPEECH OUTPUT: 'page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right arrow to next tab",
    ["BRAILLE LINE:  'Inlined Sub TabContainer page tab'",
     "     VISIBLE:  'Inlined Sub TabContainer page ta', cursor=1",
     "BRAILLE LINE:  'Inlined Sub TabContainer page tab'",
     "     VISIBLE:  'Inlined Sub TabContainer page ta', cursor=1",
     "SPEECH OUTPUT: 'Inlined Sub TabContainer'",
     "SPEECH OUTPUT: 'page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to contents",
    ["BRAILLE LINE:  'SubTab 2 page tab'",
     "     VISIBLE:  'SubTab 2 page tab', cursor=1",
     "BRAILLE LINE:  'SubTab 2 page tab'",
     "     VISIBLE:  'SubTab 2 page tab', cursor=1",
     "SPEECH OUTPUT: 'SubTab 2'",
     "SPEECH OUTPUT: 'page tab'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
