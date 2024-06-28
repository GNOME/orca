#!/usr/bin/python

"""Test of structural navigation by heading."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift+h for previous heading",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'Heading 3 h3'",
     "     VISIBLE:  'Heading 3 h3', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'Heading 3 heading level 3 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "2. Shift+h for previous heading",
    ["BRAILLE LINE:  'Heading 2 h3'",
     "     VISIBLE:  'Heading 2 h3', cursor=1",
     "SPEECH OUTPUT: 'Heading 2 heading level 3 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "3. Shift+h for previous heading",
    ["BRAILLE LINE:  'Heading 1 h3'",
     "     VISIBLE:  'Heading 1 h3', cursor=1",
     "SPEECH OUTPUT: 'Heading 1 heading level 3 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "4. h for next heading",
    ["BRAILLE LINE:  'Heading 2 h3'",
     "     VISIBLE:  'Heading 2 h3', cursor=1",
     "SPEECH OUTPUT: 'Heading 2 heading level 3 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "5. h for next heading",
    ["BRAILLE LINE:  'Heading 3 h3'",
     "     VISIBLE:  'Heading 3 h3', cursor=1",
     "SPEECH OUTPUT: 'Heading 3 heading level 3 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "6. h for next heading",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Heading 1 h3'",
     "     VISIBLE:  'Heading 1 h3', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'Heading 1 heading level 3 link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
