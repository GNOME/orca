#!/usr/bin/python

"""Test to verify presentation of the navigator."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(2000))
sequence.append(KeyComboAction("F5"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down arrow to the next item",
    ["BRAILLE LINE:  'soffice application Navigator panel Content Navigation View tree Tables collapsed'",
     "     VISIBLE:  'Tables collapsed', cursor=1",
     "SPEECH OUTPUT: 'Tables.'",
     "SPEECH OUTPUT: 'collapsed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Expand it",
    ["BRAILLE LINE:  'soffice application Navigator panel Content Navigation View tree Tables expanded'",
     "     VISIBLE:  'Tables expanded', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Collapse it",
    ["BRAILLE LINE:  'soffice application Navigator panel Content Navigation View tree Tables collapsed'",
     "     VISIBLE:  'Tables collapsed', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down arrow to the next item",
    ["BRAILLE LINE:  'soffice application Navigator panel Content Navigation View tree Text frames'",
     "     VISIBLE:  'Text frames', cursor=1",
     "SPEECH OUTPUT: 'Text frames.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
