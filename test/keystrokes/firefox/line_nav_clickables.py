#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Clickable image:'",
     "     VISIBLE:  'Clickable image:', cursor=1",
     "SPEECH OUTPUT: 'Clickable image:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Orca Logo'",
     "     VISIBLE:  'Orca Logo', cursor=1",
     "SPEECH OUTPUT: 'Orca Logo image clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'More text.'",
     "     VISIBLE:  'More text.', cursor=1",
     "SPEECH OUTPUT: 'More text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Clickable span: Click Me. More text.'",
     "     VISIBLE:  'Clickable span: Click Me. More t', cursor=1",
     "SPEECH OUTPUT: 'Clickable span:'",
     "SPEECH OUTPUT: 'Click Me. clickable'",
     "SPEECH OUTPUT: 'More text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Clickable div:'",
     "     VISIBLE:  'Clickable div:', cursor=1",
     "SPEECH OUTPUT: 'Clickable div:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6 Line Down",
    ["BRAILLE LINE:  'Click Me.'",
     "     VISIBLE:  'Click Me.', cursor=1",
     "SPEECH OUTPUT: 'Click Me. clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'More text.'",
     "     VISIBLE:  'More text.', cursor=1",
     "SPEECH OUTPUT: 'More text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Click Me.'",
     "     VISIBLE:  'Click Me.', cursor=1",
     "SPEECH OUTPUT: 'Click Me. clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'Clickable div:'",
     "     VISIBLE:  'Clickable div:', cursor=1",
     "SPEECH OUTPUT: 'Clickable div:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'Clickable span: Click Me. More text.'",
     "     VISIBLE:  'Clickable span: Click Me. More t', cursor=1",
     "SPEECH OUTPUT: 'Clickable span:'",
     "SPEECH OUTPUT: 'Click Me. clickable'",
     "SPEECH OUTPUT: 'More text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'More text.'",
     "     VISIBLE:  'More text.', cursor=1",
     "SPEECH OUTPUT: 'More text.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
