# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of the fix for one of the two issues in bug 552887a."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# Load the local test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction(utils.htmlURLPrefix + "bug-552887a.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))


########################################################################
# Down Arrow to the bottom.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "0. Line Down",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'Line 1 Line 2 h2'",
     "     VISIBLE:  'Line 1 Line 2 h2', cursor=14",
     "SPEECH OUTPUT: 'Line 1",
     "'",
     "SPEECH OUTPUT: 'Line 2",
     "'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'The Orca logo image'",
     "     VISIBLE:  'The Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'The Orca logo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4a. Line Down",
    ["KNOWN ISSUE:   We keep re-presenting this, though we're not stuck.",
     "BRAILLE LINE:  'The Orca logo image'",
     "     VISIBLE:  'The Orca logo image', cursor=0",
     "SPEECH OUTPUT: 'The Orca logo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: '",
     "'",
     "SPEECH OUTPUT: 'link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Can an Orca really'",
     "     VISIBLE:  'Can an Orca really', cursor=1",
     "SPEECH OUTPUT: 'Can an Orca really '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'hold a white cane?'",
     "     VISIBLE:  'hold a white cane?', cursor=1",
     "SPEECH OUTPUT: 'hold a white cane? '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  '\(And why aren't we'",
     "     VISIBLE:  '\(And why aren't we', cursor=1",
     "SPEECH OUTPUT: '\(And why aren't we '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'speaking this text?'",
     "     VISIBLE:  'speaking this text?', cursor=1",
     "SPEECH OUTPUT: 'speaking this text?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["KNOWN ISSUE:   We keep re-presenting this, though we're not stuck.",
     "BRAILLE LINE:  'The Orca logo image'",
     "     VISIBLE:  'The Orca logo image', cursor=0",
     "SPEECH OUTPUT: 'The Orca logo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: '",
     "'",
     "SPEECH OUTPUT: 'link image'",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'This text comes before the box section'",
     "     VISIBLE:  'This text comes before the box s', cursor=1",
     "SPEECH OUTPUT: 'This text comes before the box section",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12a. Line Down",
    ["BRAILLE LINE:  'Here's a box'",
     "     VISIBLE:  'Here's a box', cursor=1",
     "SPEECH OUTPUT: 'Here's a box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'Here's some box text.'",
     "     VISIBLE:  'Here's some box text.', cursor=1",
     "SPEECH OUTPUT: 'Here's some box text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'The end of the box'",
     "     VISIBLE:  'The end of the box', cursor=1",
     "SPEECH OUTPUT: 'The end of the box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'image This text comes after'",
     "     VISIBLE:  'image This text comes after', cursor=7",
     "SPEECH OUTPUT: 'This text comes after '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'the box section.'",
     "     VISIBLE:  'the box section.', cursor=1",
     "SPEECH OUTPUT: 'the box section.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    [""]))

########################################################################
# Up Arrow to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Up",
    ["BRAILLE LINE:  'the box section.'",
     "     VISIBLE:  'the box section.', cursor=1",
     "SPEECH OUTPUT: 'the box section.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1a. Line Up",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "2. Line Up",
#    ["BRAILLE LINE:  'This text comes after'",
#     "     VISIBLE:  'This text comes after', cursor=1",
#     "SPEECH OUTPUT: 'This text comes after'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "3. Line Up",
#    ["BRAILLE LINE:  'The end of the box'",
#     "     VISIBLE:  'The end of the box', cursor=1",
#     "SPEECH OUTPUT: 'The end of the box'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "4. Line Up",
#    ["BRAILLE LINE:  'Here's some box text.'",
#     "     VISIBLE:  'Here's some box text.', cursor=1",
#     "SPEECH OUTPUT: 'Here's some box text.'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "5. Line Up",
#    ["BRAILLE LINE:  'Here's a box'",
#     "     VISIBLE:  'Here's a box', cursor=1",
#     "SPEECH OUTPUT: 'Here's a box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'This text comes before the box section'",
     "     VISIBLE:  'This text comes before the box s', cursor=1",
     "SPEECH OUTPUT: 'This text comes before the box section",
     "'"]))

#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "8. Line Up",
#    ["BRAILLE LINE:  ''",
#     "     VISIBLE:  '', cursor=0",
#     "SPEECH OUTPUT: 'blank'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "9. Line Up",
#    ["BRAILLE LINE:  'speaking this text?'",
#     "     VISIBLE:  'speaking this text?', cursor=1",
#     "SPEECH OUTPUT: 'speaking this text?",
#     " ",
#     "'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "9a. Line Up",
#    ["BRAILLE LINE:  'why aren't we'",
#     "     VISIBLE:  'why aren't we', cursor=1",
#     "SPEECH OUTPUT: 'why aren't we'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "10. Line Up",
#    ["BRAILLE LINE:  'a white cane? (And'",
#     "     VISIBLE:  'a white cane? (And', cursor=1",
#     "SPEECH OUTPUT: 'a white cane? (And'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "11. Line Up",
#    ["BRAILLE LINE:  'Can an Orca really hold'",
#     "     VISIBLE:  'Can an Orca really hold', cursor=1",
#     "SPEECH OUTPUT: 'Can an Orca really hold'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(utils.AssertPresentationAction(
#    "12. Line Up",
#    ["BRAILLE LINE:  ''",
#     "     VISIBLE:  '', cursor=0",
#     "SPEECH OUTPUT: '",
#     " link image'"]))
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'The Orca logo image'",
     "     VISIBLE:  'The Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'The Orca logo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'Line 1 Line 2 h2'",
     "     VISIBLE:  'Line 1 Line 2 h2', cursor=1",
     "SPEECH OUTPUT: 'Line 1",
     "'",
     "SPEECH OUTPUT: 'Line 2",
     "'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
