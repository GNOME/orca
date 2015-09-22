#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(WaitForDocLoad())

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>Home"))

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
     "SPEECH OUTPUT: 'Science link heading level 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Recent Tags h4'",
     "     VISIBLE:  'Recent Tags h4', cursor=1",
     "SPEECH OUTPUT: 'Recent Tags link heading level 4.'"]))

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
    ["BRAILLE LINE:  'Nickname $l Password $l Log in push button'",
     "     VISIBLE:  'Nickname $l Password $l Log in p', cursor=1",
     "SPEECH OUTPUT: 'Nickname'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'Password'",
     "SPEECH OUTPUT: 'password text'",
     "SPEECH OUTPUT: 'Log in push button'"]))

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
     "SPEECH OUTPUT: 'What is your favorite poison?"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  '& y Some polls radio button'",
     "     VISIBLE:  '& y Some polls radio button', cursor=1",
     "SPEECH OUTPUT: 'Some polls.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Book Reviews h4'",
     "     VISIBLE:  'Book Reviews h4', cursor=1",
     "SPEECH OUTPUT: 'Book Reviews link heading level 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  '& y Some polls radio button'",
     "     VISIBLE:  '& y Some polls radio button', cursor=1",
     "SPEECH OUTPUT: 'Some polls.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'What is your favorite poison?'",
     "     VISIBLE:  'What is your favorite poison?', cursor=1",
     "SPEECH OUTPUT: 'What is your favorite poison?"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'Some Poll h4'",
     "     VISIBLE:  'Some Poll h4', cursor=1",
     "SPEECH OUTPUT: 'Some Poll heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'Nickname $l Password $l Log in push button'",
     "     VISIBLE:  'Nickname $l Password $l Log in p', cursor=1",
     "SPEECH OUTPUT: 'Nickname'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'Password'",
     "SPEECH OUTPUT: 'password text'",
     "SPEECH OUTPUT: 'Log in push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'Slashdot Login h4'",
     "     VISIBLE:  'Slashdot Login h4', cursor=1",
     "SPEECH OUTPUT: 'Slashdot Login heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'Recent Tags h4'",
     "     VISIBLE:  'Recent Tags h4', cursor=1",
     "SPEECH OUTPUT: 'Recent Tags link heading level 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  'Science h4'",
     "     VISIBLE:  'Science h4', cursor=1",
     "SPEECH OUTPUT: 'Science link heading level 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  'Services h4'",
     "     VISIBLE:  'Services h4', cursor=1",
     "SPEECH OUTPUT: 'Services heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  'About h4'",
     "     VISIBLE:  'About h4', cursor=1",
     "SPEECH OUTPUT: 'About heading level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  'Stories h4'",
     "     VISIBLE:  'Stories h4', cursor=1",
     "SPEECH OUTPUT: 'Stories heading level 4'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
