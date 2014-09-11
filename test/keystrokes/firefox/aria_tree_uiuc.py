#!/usr/bin/python

"""Test of UIUC tree presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to tree",
    ["BRAILLE LINE:  'Fruits expanded list item'",
     "     VISIBLE:  'Fruits expanded list item', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Fruits'",
     "SPEECH OUTPUT: 'expanded tree level 1'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereAmI",
    ["BRAILLE LINE:  'Fruits expanded list item'",
     "     VISIBLE:  'Fruits expanded list item', cursor=1",
     "BRAILLE LINE:  'Fruits expanded list item'",
     "     VISIBLE:  'Fruits expanded list item', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Fruits'",
     "SPEECH OUTPUT: '1 of 2 expanded tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down arrow to oranges",
    ["BRAILLE LINE:  'Oranges list item'",
     "     VISIBLE:  'Oranges list item', cursor=1",
     "BRAILLE LINE:  'Oranges list item'",
     "     VISIBLE:  'Oranges list item', cursor=1",
     "SPEECH OUTPUT: 'Oranges'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down arrow to pineapples",
    ["BRAILLE LINE:  'Pineapples list item'",
     "     VISIBLE:  'Pineapples list item', cursor=1",
     "BRAILLE LINE:  'Pineapples list item'",
     "     VISIBLE:  'Pineapples list item', cursor=1",
     "SPEECH OUTPUT: 'Pineapples'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down arrow to apples",
    ["BRAILLE LINE:  'Apples collapsed list item'",
     "     VISIBLE:  'Apples collapsed list item', cursor=1",
     "SPEECH OUTPUT: 'Apples'",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Expand apples",
    ["BRAILLE LINE:  'Apples expanded list item'",
     "     VISIBLE:  'Apples expanded list item', cursor=1",
     "BRAILLE LINE:  'Apples expanded list item'",
     "     VISIBLE:  'Apples expanded list item', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down arrow to macintosh",
    ["BRAILLE LINE:  'Macintosh list item'",
     "     VISIBLE:  'Macintosh list item', cursor=1",
     "BRAILLE LINE:  'Macintosh list item'",
     "     VISIBLE:  'Macintosh list item', cursor=1",
     "SPEECH OUTPUT: 'Macintosh'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down arrow to granny smith",
    ["BRAILLE LINE:  'Granny Smith collapsed list item'",
     "     VISIBLE:  'Granny Smith collapsed list item', cursor=1",
     "SPEECH OUTPUT: 'Granny Smith'",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "9. Expand granny smith",
    ["BRAILLE LINE:  'Granny Smith expanded list item'",
     "     VISIBLE:  'Granny Smith expanded list item', cursor=1",
     "BRAILLE LINE:  'Granny Smith expanded list item'",
     "     VISIBLE:  'Granny Smith expanded list item', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down arrow to washington state",
    ["BRAILLE LINE:  'Washington State list item'",
     "     VISIBLE:  'Washington State list item', cursor=1",
     "BRAILLE LINE:  'Washington State list item'",
     "     VISIBLE:  'Washington State list item', cursor=1",
     "SPEECH OUTPUT: 'Washington State'",
     "SPEECH OUTPUT: 'tree level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down arrow to michigan",
    ["BRAILLE LINE:  'Michigan list item'",
     "     VISIBLE:  'Michigan list item', cursor=1",
     "BRAILLE LINE:  'Michigan list item'",
     "     VISIBLE:  'Michigan list item', cursor=1",
     "SPEECH OUTPUT: 'Michigan'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down arrow to new york",
    ["BRAILLE LINE:  'New York list item'",
     "     VISIBLE:  'New York list item', cursor=1",
     "BRAILLE LINE:  'New York list item'",
     "     VISIBLE:  'New York list item', cursor=1",
     "SPEECH OUTPUT: 'New York'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Down arrow to fuji",
    ["BRAILLE LINE:  'Fuji list item'",
     "     VISIBLE:  'Fuji list item', cursor=1",
     "BRAILLE LINE:  'Fuji list item'",
     "     VISIBLE:  'Fuji list item', cursor=1",
     "SPEECH OUTPUT: 'Fuji'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Down arrow to bananas",
    ["BRAILLE LINE:  'Bananas list item'",
     "     VISIBLE:  'Bananas list item', cursor=1",
     "BRAILLE LINE:  'Bananas list item'",
     "     VISIBLE:  'Bananas list item', cursor=1",
     "SPEECH OUTPUT: 'Bananas'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Down arrow to pears",
    ["BRAILLE LINE:  'Pears list item'",
     "     VISIBLE:  'Pears list item', cursor=1",
     "BRAILLE LINE:  'Pears list item'",
     "     VISIBLE:  'Pears list item', cursor=1",
     "SPEECH OUTPUT: 'Pears'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Down arrow to vegetables",
    ["BRAILLE LINE:  'Vegetables expanded list item'",
     "     VISIBLE:  'Vegetables expanded list item', cursor=1",
     "SPEECH OUTPUT: 'Vegetables'",
     "SPEECH OUTPUT: 'expanded tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Collapse vegetables",
    ["BRAILLE LINE:  'Vegetables collapsed list item'",
     "     VISIBLE:  'Vegetables collapsed list item', cursor=1",
     "BRAILLE LINE:  'Vegetables collapsed list item'",
     "     VISIBLE:  'Vegetables collapsed list item', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
