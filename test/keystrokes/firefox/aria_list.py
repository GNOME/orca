#!/usr/bin/python

"""Test of presentation of ARIA role list."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow",
    ["KNOWN ISSUE: We're moving to the end of this line and getting stuck",
     "BRAILLE LINE:  'dog'",
     "     VISIBLE:  'dog', cursor=1",
     "SPEECH OUTPUT: 'dog'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["KNOWN ISSUE: We're moving to the end of this line and getting stuck",
     "BRAILLE LINE:  'dog'",
     "     VISIBLE:  'dog', cursor=1",
     "SPEECH OUTPUT: 'dog'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic whereAmI",
    ["KNOWN ISSUE: We're moving to the end of this line and getting stuck",
     "BRAILLE LINE:  'dog'",
     "     VISIBLE:  'dog', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'dog'",
     "SPEECH OUTPUT: '1 of 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow",
    ["KNOWN ISSUE: We're moving to the end of this line and getting stuck",
     "BRAILLE LINE:  'dog'",
     "     VISIBLE:  'dog', cursor=1",
     "SPEECH OUTPUT: 'dog'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
