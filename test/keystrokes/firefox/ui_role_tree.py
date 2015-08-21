#!/usr/bin/python

"""Test of tree output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Alt>b"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift Tab for tree",
    ["BRAILLE LINE:  'Firefox application Library frame All Bookmarks expanded list item TREE LEVEL 1'",
     "     VISIBLE:  'All Bookmarks expanded list item', cursor=1",
     "SPEECH OUTPUT: 'All Bookmarks.'",
     "SPEECH OUTPUT: 'expanded.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow in tree",
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Toolbar collapsed list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Toolbar collapsed list', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Toolbar.'",
     "SPEECH OUTPUT: 'collapsed.'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow in tree",
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Menu collapsed list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Menu collapsed list it', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Menu.'",
     "SPEECH OUTPUT: 'collapsed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Basic Where Am I", 
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Menu collapsed list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Menu collapsed list it', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: 'Bookmarks Menu.'",
     "SPEECH OUTPUT: '2 of 3.'",
     "SPEECH OUTPUT: 'collapsed tree level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right Arrow to expand folder", 
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Menu expanded list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Menu expanded list ite', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Basic Where Am I", 
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Menu expanded list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Menu expanded list ite', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: 'Bookmarks Menu.'",
     "SPEECH OUTPUT: '2 of 3.'",
     "SPEECH OUTPUT: 'expanded tree level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down Arrow in tree",
    ["BRAILLE LINE:  'Firefox application Library frame Recently Bookmarked list item TREE LEVEL 3'",
     "     VISIBLE:  'Recently Bookmarked list item TR', cursor=1",
     "SPEECH OUTPUT: 'Recently Bookmarked.'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. Basic Where Am I", 
    ["BRAILLE LINE:  'Firefox application Library frame Recently Bookmarked list item TREE LEVEL 3'",
     "     VISIBLE:  'Recently Bookmarked list item TR', cursor=1",
     "SPEECH OUTPUT: 'list item.'",
     "SPEECH OUTPUT: 'Recently Bookmarked.'",
     "SPEECH OUTPUT: '1 of 4.'",
     "SPEECH OUTPUT: 'tree level 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Up Arrow in tree",
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Menu expanded list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Menu expanded list ite', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Menu.'",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Left Arrow to collapse folder", 
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Menu collapsed list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Menu collapsed list it', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Up Arrow in tree",
    ["BRAILLE LINE:  'Firefox application Library frame Bookmarks Toolbar collapsed list item TREE LEVEL 2'",
     "     VISIBLE:  'Bookmarks Toolbar collapsed list', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Toolbar.'",
     "SPEECH OUTPUT: 'collapsed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Up Arrow in tree",
    ["BRAILLE LINE:  'Firefox application Library frame All Bookmarks expanded list item TREE LEVEL 1'",
     "     VISIBLE:  'All Bookmarks expanded list item', cursor=1",
     "SPEECH OUTPUT: 'All Bookmarks.'",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "13. Tab back to tree table",
    ["BRAILLE LINE:  'Firefox application Library frame tree table Bookmarks Toolbar   table row TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Toolbar   table row TR', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Toolbar   table row'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
