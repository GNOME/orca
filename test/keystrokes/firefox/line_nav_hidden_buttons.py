#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'The start'",
     "     VISIBLE:  'The start', cursor=1",
     "SPEECH OUTPUT: 'The start'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Button1 push button Button 2 push button'",
     "     VISIBLE:  'Button1 push button Button 2 pus', cursor=1",
     "SPEECH OUTPUT: 'Button1 push button'",
     "SPEECH OUTPUT: 'Button 2 push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'The end'",
     "     VISIBLE:  'The end', cursor=1",
     "SPEECH OUTPUT: 'The end'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'Button1 push button Button 2 push button'",
     "     VISIBLE:  'Button1 push button Button 2 pus', cursor=1",
     "SPEECH OUTPUT: 'Button1 push button'",
     "SPEECH OUTPUT: 'Button 2 push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'The start'",
     "     VISIBLE:  'The start', cursor=1",
     "SPEECH OUTPUT: 'The start'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
