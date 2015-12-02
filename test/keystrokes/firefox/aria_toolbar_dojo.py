#!/usr/bin/python

"""Test of Dojo toolbar presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Ctrl + Home",
    ["BRAILLE LINE:  'Toolbar test h1'",
     "     VISIBLE:  'Toolbar test h1', cursor=1",
     "SPEECH OUTPUT: 'Toolbar test heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["BRAILLE LINE:  'Toolbar from markup h2'",
     "     VISIBLE:  'Toolbar from markup h2', cursor=1",
     "SPEECH OUTPUT: 'Toolbar from markup heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["BRAILLE LINE:  'input before toolbar1 $l'",
     "     VISIBLE:  'input before toolbar1 $l', cursor=1",
     "SPEECH OUTPUT: 'entry input before toolbar1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow",
    ["BRAILLE LINE:  'tool bar'",
     "     VISIBLE:  'tool bar', cursor=1",
     "SPEECH OUTPUT: 'tool bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow",
    ["BRAILLE LINE:  'input after toolbar1 $l'",
     "     VISIBLE:  'input after toolbar1 $l', cursor=1",
     "SPEECH OUTPUT: 'entry input after toolbar1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
