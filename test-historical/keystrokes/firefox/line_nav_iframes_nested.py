#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  '\\+1 push button [0-9]+'",
     "     VISIBLE:  '\\+1 push button [0-9]+', cursor=1",
     "SPEECH OUTPUT: '\\+1 push button'",
     "SPEECH OUTPUT: '[0-9]+'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'After the iframe'",
     "     VISIBLE:  'After the iframe', cursor=1",
     "SPEECH OUTPUT: 'After the iframe'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "3. Top of file",
    ["BRAILLE LINE:  '\\+1 push button [0-9]+'",
     "     VISIBLE:  '\\+1 push button [0-9]+', cursor=1",
     "SPEECH OUTPUT: '\\+1 push button'",
     "SPEECH OUTPUT: '[0-9]+'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'After the iframe'",
     "     VISIBLE:  'After the iframe', cursor=1",
     "SPEECH OUTPUT: 'After the iframe'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
