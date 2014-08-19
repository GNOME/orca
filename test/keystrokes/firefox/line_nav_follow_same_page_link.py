#!/usr/bin/python

"""Test of navigation to same page links."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Contents h1'",
     "     VISIBLE:  'Contents h1', cursor=1",
     "SPEECH OUTPUT: 'Contents'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  '•First item'",
     "     VISIBLE:  '•First item', cursor=2",
     "BRAILLE LINE:  '•First item'",
     "     VISIBLE:  '•First item', cursor=2",
     "SPEECH OUTPUT: 'First item'",
     "SPEECH OUTPUT: 'link' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  '•Second item'",
     "     VISIBLE:  '•Second item', cursor=2",
     "BRAILLE LINE:  '•Second item'",
     "     VISIBLE:  '•Second item', cursor=2",
     "SPEECH OUTPUT: 'Second item'",
     "SPEECH OUTPUT: 'link' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "4. Return",
    ["BRAILLE LINE:  '•Second item'",
     "     VISIBLE:  '•Second item', cursor=2",
     "BRAILLE LINE:  'seas. '",
     "     VISIBLE:  'seas. ', cursor=7",
     "SPEECH OUTPUT: 'link' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down",
    ["BRAILLE LINE:  'Second h2'",
     "     VISIBLE:  'Second h2', cursor=1",
     "SPEECH OUTPUT: 'Second'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
