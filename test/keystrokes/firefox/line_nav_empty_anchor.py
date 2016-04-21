#!/usr/bin/python

"""Test of line navigation on a page with empty anchors."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'FAQ  h1'",
     "     VISIBLE:  'FAQ  h1', cursor=1",
     "SPEECH OUTPUT: 'FAQ'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Q. What's a battery?'",
     "     VISIBLE:  'Q. What's a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What's a battery?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page?'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'FOO h2'",
     "     VISIBLE:  'FOO h2', cursor=1",
     "SPEECH OUTPUT: 'FOO'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Q. Why would someone put a line break in a heading?'",
     "     VISIBLE:  'Q. Why would someone put a line ', cursor=1",
     "SPEECH OUTPUT: 'Q. Why would someone put a line break in a heading?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'Q. What is the airspeed velocity of an unladen swallow?'",
     "     VISIBLE:  'Q. What is the airspeed velocity', cursor=1",
     "SPEECH OUTPUT: 'Q. What is the airspeed velocity of an unladen swallow?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Q. What is a battery?'",
     "     VISIBLE:  'Q. What is a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What is a battery?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'A. Look it up.'",
     "     VISIBLE:  'A. Look it up.', cursor=1",
     "SPEECH OUTPUT: 'A. Look it up.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'A. That way.'",
     "     VISIBLE:  'A. That way.', cursor=1",
     "SPEECH OUTPUT: 'A. That way.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page?'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'A. Empty anchors.'",
     "     VISIBLE:  'A. Empty anchors.', cursor=1",
     "SPEECH OUTPUT: 'A. Empty anchors.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page?'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  'A. That way.'",
     "     VISIBLE:  'A. That way.', cursor=1",
     "SPEECH OUTPUT: 'A. That way.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  'A. Look it up.'",
     "     VISIBLE:  'A. Look it up.', cursor=1",
     "SPEECH OUTPUT: 'A. Look it up.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  'Q. What is a battery?'",
     "     VISIBLE:  'Q. What is a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What is a battery?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Up",
    ["BRAILLE LINE:  'Q. What is the airspeed velocity of an unladen swallow?'",
     "     VISIBLE:  'Q. What is the airspeed velocity', cursor=1",
     "SPEECH OUTPUT: 'Q. What is the airspeed velocity of an unladen swallow?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Up",
    ["BRAILLE LINE:  'Q. Why would someone put a line break in a heading?'",
     "     VISIBLE:  'Q. Why would someone put a line ', cursor=1",
     "SPEECH OUTPUT: 'Q. Why would someone put a line break in a heading?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Up",
    ["BRAILLE LINE:  'FOO h2'",
     "     VISIBLE:  'FOO h2', cursor=1",
     "SPEECH OUTPUT: 'FOO'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page?'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Up",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Up",
    ["BRAILLE LINE:  'Q. What's a battery?'",
     "     VISIBLE:  'Q. What's a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What's a battery?'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Up",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'FAQ  h1'",
     "     VISIBLE:  'FAQ  h1', cursor=1",
     "SPEECH OUTPUT: 'FAQ'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
