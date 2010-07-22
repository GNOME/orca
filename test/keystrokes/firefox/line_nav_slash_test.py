# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "slash-test.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Stories h4'",
     "     VISIBLE:  'Stories h4', cursor=1",
     "SPEECH OUTPUT: 'Stories heading level 4'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'About h4'",
     "     VISIBLE:  'About h4', cursor=1",
     "SPEECH OUTPUT: 'About heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Services h4'",
     "     VISIBLE:  'Services h4', cursor=1",
     "SPEECH OUTPUT: 'Services heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Science h4'",
     "     VISIBLE:  'Science h4', cursor=1",
     "SPEECH OUTPUT: 'Science link heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Recent Tags h4'",
     "     VISIBLE:  'Recent Tags h4', cursor=1",
     "SPEECH OUTPUT: 'Recent Tags link heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Slashdot Login h4'",
     "     VISIBLE:  'Slashdot Login h4', cursor=1",
     "SPEECH OUTPUT: 'Slashdot Login heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Nickname  $l Password  $l Log in Button'",
     "     VISIBLE:  'Nickname  $l Password  $l Log in', cursor=1",
     "SPEECH OUTPUT: 'Nickname text Password password Log in button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Some Poll h4'",
     "     VISIBLE:  'Some Poll h4', cursor=1",
     "SPEECH OUTPUT: 'Some Poll heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'What is your favorite poison?'",
     "     VISIBLE:  'What is your favorite poison?', cursor=1",
     "SPEECH OUTPUT: 'What is your favorite poison?",
     " panel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["KNOWN ISSUE - Sometimes we also say 'Recent Tags'. Might be a timing issue.",
     "BRAILLE LINE:  '& y RadioButton Some polls'",
     "     VISIBLE:  '& y RadioButton Some polls', cursor=1",
     "SPEECH OUTPUT: 'Some polls not selected radio button'",
     "SPEECH OUTPUT: 'Recent Tags'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Book Reviews h4'",
     "     VISIBLE:  'Book Reviews h4', cursor=1",
     "SPEECH OUTPUT: 'Book Reviews link heading level 4'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Up",
    ["BRAILLE LINE:  '& y RadioButton Some polls'",
     "     VISIBLE:  '& y RadioButton Some polls', cursor=1",
     "SPEECH OUTPUT: 'Some polls not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Up",
    ["BRAILLE LINE:  'What is your favorite poison?'",
     "     VISIBLE:  'What is your favorite poison?', cursor=1",
     "SPEECH OUTPUT: 'What is your favorite poison?",
     " panel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  'Some Poll h4'",
     "     VISIBLE:  'Some Poll h4', cursor=1",
     "SPEECH OUTPUT: 'Some Poll heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'Nickname  $l Password  $l Log in Button'",
     "     VISIBLE:  'Nickname  $l Password  $l Log in', cursor=1",
     "SPEECH OUTPUT: 'Nickname text Password password Log in button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'Slashdot Login h4'",
     "     VISIBLE:  'Slashdot Login h4', cursor=1",
     "SPEECH OUTPUT: 'Slashdot Login heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'Recent Tags h4'",
     "     VISIBLE:  'Recent Tags h4', cursor=1",
     "SPEECH OUTPUT: 'Recent Tags link heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Science h4'",
     "     VISIBLE:  'Science h4', cursor=1",
     "SPEECH OUTPUT: 'Science link heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Services h4'",
     "     VISIBLE:  'Services h4', cursor=1",
     "SPEECH OUTPUT: 'Services heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'About h4'",
     "     VISIBLE:  'About h4', cursor=1",
     "SPEECH OUTPUT: 'About heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'Stories h4'",
     "     VISIBLE:  'Stories h4', cursor=1",
     "SPEECH OUTPUT: 'Stories heading level 4'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
