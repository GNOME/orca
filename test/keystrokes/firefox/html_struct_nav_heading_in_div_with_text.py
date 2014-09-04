#!/usr/bin/python

"""Test of structural navigation by blockquote."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("2"))
sequence.append(utils.AssertPresentationAction(
    "1. 2 for first heading", 
    ["BRAILLE LINE:  'First Heading h2'",
     "     VISIBLE:  'First Heading h2', cursor=1",
     "SPEECH OUTPUT: 'First Heading '",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow to text", 
    ["BRAILLE LINE:  'text'",
     "     VISIBLE:  'text', cursor=1",
     "SPEECH OUTPUT: 'text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("2"))
sequence.append(utils.AssertPresentationAction(
    "3. 2 for second heading", 
    ["KNOWN ISSUE: This is not the second heading. We looped.",
     "BRAILLE LINE:  'First Heading h2'",
     "     VISIBLE:  'First Heading h2', cursor=1",
     "SPEECH OUTPUT: 'First Heading '",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
