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
    ["BRAILLE LINE:  'this is a page to test how well Orca works with list items.'",
     "     VISIBLE:  'this is a page to test how well ', cursor=1",
     "SPEECH OUTPUT: 'this is a page to test how well Orca works with list items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'this is an ordered list:'",
     "     VISIBLE:  'this is an ordered list:', cursor=1",
     "SPEECH OUTPUT: 'this is an ordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=1",
     "SPEECH OUTPUT: '1. This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read'",
     "     VISIBLE:  '2. This is a list item that span', cursor=1",
     "SPEECH OUTPUT: '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that'",
     "     VISIBLE:  'several lines of text within thi', cursor=1",
     "SPEECH OUTPUT: 'several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'should probably be put out of its misery.'",
     "     VISIBLE:  'should probably be put out of it', cursor=1",
     "SPEECH OUTPUT: 'should probably be put out of its misery.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'This is an example of an unordered list:'",
     "     VISIBLE:  'This is an example of an unorder', cursor=1",
     "SPEECH OUTPUT: 'This is an example of an unordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  '• This is a short list item.'",
     "     VISIBLE:  '• This is a short list item.', cursor=1",
     "SPEECH OUTPUT: '• This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  '• This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read'",
     "     VISIBLE:  '• This is a list item that spans', cursor=1",
     "SPEECH OUTPUT: '• This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that'",
     "     VISIBLE:  'several lines of text within thi', cursor=1",
     "SPEECH OUTPUT: 'several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  '• This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read'",
     "     VISIBLE:  '• This is a list item that spans', cursor=1",
     "SPEECH OUTPUT: '• This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  '• This is a short list item.'",
     "     VISIBLE:  '• This is a short list item.', cursor=1",
     "SPEECH OUTPUT: '• This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'This is an example of an unordered list:'",
     "     VISIBLE:  'This is an example of an unorder', cursor=1",
     "SPEECH OUTPUT: 'This is an example of an unordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'should probably be put out of its misery.'",
     "     VISIBLE:  'should probably be put out of it', cursor=1",
     "SPEECH OUTPUT: 'should probably be put out of its misery.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that'",
     "     VISIBLE:  'several lines of text within thi', cursor=1",
     "SPEECH OUTPUT: 'several lines of text within this single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read'",
     "     VISIBLE:  '2. This is a list item that span', cursor=1",
     "SPEECH OUTPUT: '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=1",
     "SPEECH OUTPUT: '1. This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  'this is an ordered list:'",
     "     VISIBLE:  'this is an ordered list:', cursor=1",
     "SPEECH OUTPUT: 'this is an ordered list:'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
