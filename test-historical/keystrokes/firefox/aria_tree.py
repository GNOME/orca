#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to tree",
    ["BRAILLE LINE:  'embedded'",
     "     VISIBLE:  'embedded', cursor=1",
     "BRAILLE LINE:  'Fruits expanded'",
     "     VISIBLE:  'Fruits expanded', cursor=1",
     "SPEECH OUTPUT: 'Fruits.'",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereAmI",
    ["BRAILLE LINE:  'Fruits expanded'",
     "     VISIBLE:  'Fruits expanded', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: 'Fruits.'",
     "SPEECH OUTPUT: '1 of 2.'",
     "SPEECH OUTPUT: 'expanded tree level 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down arrow to oranges",
    ["BRAILLE LINE:  'Oranges list item'",
     "     VISIBLE:  'Oranges list item', cursor=1",
     "SPEECH OUTPUT: 'Oranges.'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down arrow to pineapples",
    ["BRAILLE LINE:  'Pineapples list item'",
     "     VISIBLE:  'Pineapples list item', cursor=1",
     "SPEECH OUTPUT: 'Pineapples.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down arrow to apples",
    ["BRAILLE LINE:  'Apples collapsed'",
     "     VISIBLE:  'Apples collapsed', cursor=1",
     "SPEECH OUTPUT: 'Apples.'",
     "SPEECH OUTPUT: 'collapsed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Expand apples",
    ["BRAILLE LINE:  'Apples expanded'",
     "     VISIBLE:  'Apples expanded', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down arrow to macintosh",
    ["BRAILLE LINE:  'Macintosh list item'",
     "     VISIBLE:  'Macintosh list item', cursor=1",
     "SPEECH OUTPUT: 'Macintosh.'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down arrow to granny smith",
    ["BRAILLE LINE:  'Granny Smith collapsed'",
     "     VISIBLE:  'Granny Smith collapsed', cursor=1",
     "SPEECH OUTPUT: 'Granny Smith.'",
     "SPEECH OUTPUT: 'collapsed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "9. Expand granny smith",
    ["BRAILLE LINE:  'Granny Smith expanded'",
     "     VISIBLE:  'Granny Smith expanded', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down arrow to washington state",
    ["BRAILLE LINE:  'Washington State list item'",
     "     VISIBLE:  'Washington State list item', cursor=1",
     "SPEECH OUTPUT: 'Washington State.'",
     "SPEECH OUTPUT: 'tree level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down arrow to michigan",
    ["BRAILLE LINE:  'Michigan list item'",
     "     VISIBLE:  'Michigan list item', cursor=1",
     "SPEECH OUTPUT: 'Michigan.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down arrow to new york",
    ["BRAILLE LINE:  'New York list item'",
     "     VISIBLE:  'New York list item', cursor=1",
     "SPEECH OUTPUT: 'New York.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Down arrow to fuji",
    ["BRAILLE LINE:  'Fuji list item'",
     "     VISIBLE:  'Fuji list item', cursor=1",
     "SPEECH OUTPUT: 'Fuji.'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Down arrow to bananas",
    ["BRAILLE LINE:  'Bananas list item'",
     "     VISIBLE:  'Bananas list item', cursor=1",
     "SPEECH OUTPUT: 'Bananas.'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Down arrow to pears",
    ["BRAILLE LINE:  'Pears list item'",
     "     VISIBLE:  'Pears list item', cursor=1",
     "SPEECH OUTPUT: 'Pears.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Down arrow to vegetables",
    ["BRAILLE LINE:  'Vegetables expanded'",
     "     VISIBLE:  'Vegetables expanded', cursor=1",
     "SPEECH OUTPUT: 'Vegetables.'",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Collapse vegetables",
    ["BRAILLE LINE:  'Vegetables collapsed'",
     "     VISIBLE:  'Vegetables collapsed', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
