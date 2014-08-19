#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Holiday Gift Giving'",
     "     VISIBLE:  'Holiday Gift Giving', cursor=1",
     "SPEECH OUTPUT: 'Holiday Gift Giving'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Shop Early - Deliver Later'",
     "     VISIBLE:  'Shop Early - Deliver Later', cursor=1",
     "SPEECH OUTPUT: 'Shop Early - Deliver Later",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'The Ideal Gift Collection'",
     "     VISIBLE:  'The Ideal Gift Collection', cursor=1",
     "SPEECH OUTPUT: 'The Ideal Gift Collection'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["KNOWN ISSUE: There is currently a Gecko bug or two that make the results get odd/off around here.",
     "BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  '  2 (5 oz.) Filet Mignons'",
     "     VISIBLE:  '  2 (5 oz.) Filet Mignons', cursor=0",
     "SPEECH OUTPUT: '  2 (5 oz.) Filet Mignons",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  '  2 (5 oz.) Top Sirloins'",
     "     VISIBLE:  '  2 (5 oz.) Top Sirloins', cursor=0",
     "SPEECH OUTPUT: '  2 (5 oz.) Top Sirloins",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  '  4 (4 oz.) Foobar Steaks Burgers'",
     "     VISIBLE:  '  4 (4 oz.) Foobar Steaks Burger', cursor=0",
     "SPEECH OUTPUT: '  4 (4 oz.) Foobar Steaks Burgers",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  '  6 (5.75 oz.) Stuffed Baked Potatoes'",
     "     VISIBLE:  '  6 (5.75 oz.) Stuffed Baked Pot', cursor=0",
     "SPEECH OUTPUT: '  6 (5.75 oz.) Stuffed Baked Potatoes",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  '  2 (4.5 oz.) Stuffed Sole with Scallops and Crab'",
     "     VISIBLE:  '  2 (4.5 oz.) Stuffed Sole with ', cursor=0",
     "SPEECH OUTPUT: '  2 (4.5 oz.) Stuffed Sole with Scallops and Crab",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  '  1 (6 in.) Chocolate Lover's Cake",
     "Regular $133.00, Now $59.99'",
     "     VISIBLE:  '(6 in.) Chocolate Lover's Cake",
     "R', cursor=32",
     "SPEECH OUTPUT: '  1 (6 in.) Chocolate Lover's Cake",
     "Regular $133.00, Now $59.99",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["KNOWN ISSUE: We skip lines on the way up so the results which follow are broken.",
     "BRAILLE LINE:  '  6 (5.75 oz.) Stuffed Baked Potatoes'",
     "     VISIBLE:  '  6 (5.75 oz.) Stuffed Baked Pot', cursor=0",
     "SPEECH OUTPUT: '  6 (5.75 oz.) Stuffed Baked Potatoes",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  '  2 (5 oz.) Top Sirloins'",
     "     VISIBLE:  '  2 (5 oz.) Top Sirloins', cursor=0",
     "SPEECH OUTPUT: '  2 (5 oz.) Top Sirloins",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  'The Ideal Gift Collection'",
     "     VISIBLE:  'The Ideal Gift Collection', cursor=1",
     "SPEECH OUTPUT: 'The Ideal Gift Collection'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  'Shop Early - Deliver Later'",
     "     VISIBLE:  'Shop Early - Deliver Later', cursor=1",
     "SPEECH OUTPUT: 'Shop Early - Deliver Later",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  'Holiday Gift Giving'",
     "     VISIBLE:  'Holiday Gift Giving', cursor=1",
     "SPEECH OUTPUT: 'Holiday Gift Giving'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
