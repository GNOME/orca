#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=0",
     "SPEECH OUTPUT: 'foo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["KNOWN ISSUE: We're re-presenting the image",
     "BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=0",
     "SPEECH OUTPUT: 'foo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' Before '",
     "SPEECH OUTPUT: 'Line'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' After",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["KNOWN ISSUE: We're getting stuck here",
     "BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=0",
     "SPEECH OUTPUT: 'foo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' Before '",
     "SPEECH OUTPUT: 'Line'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' After",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "5. End of file",
    ["BRAILLE LINE:  'End'",
     "     VISIBLE:  'End', cursor=3",
     "SPEECH OUTPUT: 'End'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=0",
     "SPEECH OUTPUT: 'foo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' Before '",
     "SPEECH OUTPUT: 'Line'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' After",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
