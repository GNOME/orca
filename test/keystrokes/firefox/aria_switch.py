#!/usr/bin/python

"""Test of ARIA switch presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to switch",
    ["BRAILLE LINE:  '& y Power saving switch'",
     "     VISIBLE:  '& y Power saving switch', cursor=1",
     "SPEECH OUTPUT: 'Power saving switch off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "2. Change state of switch",
    ["BRAILLE LINE:  '&=y Power saving switch'",
     "     VISIBLE:  '&=y Power saving switch', cursor=1",
     "SPEECH OUTPUT: 'on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "3. Change state of switch",
    ["BRAILLE LINE:  '& y Power saving switch'",
     "     VISIBLE:  '& y Power saving switch', cursor=1",
     "SPEECH OUTPUT: 'off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Basic whereAmI",
    ["BRAILLE LINE:  '& y Power saving switch'",
     "     VISIBLE:  '& y Power saving switch', cursor=1",
     "SPEECH OUTPUT: 'Power saving switch off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up arrow",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down arrow",
    ["BRAILLE LINE:  'Line 2: & y Power saving switch'",
     "     VISIBLE:  'Line 2: & y Power saving switch', cursor=1",
     "SPEECH OUTPUT: 'Line 2:'",
     "SPEECH OUTPUT: 'Power saving switch off'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
