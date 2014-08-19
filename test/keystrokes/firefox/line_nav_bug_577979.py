#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'this is a page to test how well Orca works with list items.'",
     "     VISIBLE:  'this is a page to test how well ', cursor=1",
     "SPEECH OUTPUT: 'this is a page to test how well Orca works with list items. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'this is an ordered list:'",
     "     VISIBLE:  'this is an ordered list:', cursor=1",
     "SPEECH OUTPUT: 'this is an ordered list: '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  '1.This is a short list item.'",
     "     VISIBLE:  '1.This is a short list item.', cursor=3",
     "SPEECH OUTPUT: '1.This is a short list item. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '2.This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have'",
     "     VISIBLE:  '2.This is a list item that spans', cursor=3",
     "SPEECH OUTPUT: '2.This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Next Word",
    ["BRAILLE LINE:  '2.This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have'",
     "     VISIBLE:  '2.This is a list item that spans', cursor=7",
     "SPEECH OUTPUT: 'This '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Next Word",
    ["BRAILLE LINE:  '2.This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have'",
     "     VISIBLE:  '2.This is a list item that spans', cursor=10",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "7. Next Word",
    ["BRAILLE LINE:  '2.This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have'",
     "     VISIBLE:  '2.This is a list item that spans', cursor=12",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "8. Next Word",
    ["BRAILLE LINE:  '2.This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have'",
     "     VISIBLE:  '2.This is a list item that spans', cursor=17",
     "SPEECH OUTPUT: 'list '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'read several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is'",
     "     VISIBLE:  'read several lines of text withi', cursor=1",
     "SPEECH OUTPUT: 'read several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
