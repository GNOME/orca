#!/usr/bin/python

"""Test of structural navigation by heading."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "1. h for next heading",
    ["KNOWN ISSUE: Speech is broken",
     "BRAILLE LINE:  'line 2 h1'",
     "     VISIBLE:  'line 2 h1', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "2. h for next heading",
    ["KNOWN ISSUE: Speech is broken",
     "BRAILLE LINE:  'line 3 h1'",
     "     VISIBLE:  'line 3 h1', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "3. h for next heading",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
