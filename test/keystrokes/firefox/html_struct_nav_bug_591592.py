#!/usr/bin/python

"""Test of table structural navigation with headings which contain anchors."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This is a test. h1'",
     "     VISIBLE:  'This is a test. h1', cursor=1",
     "SPEECH OUTPUT: 'This is a test. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "2. h",
    ["BRAILLE LINE:  'Adding IPS Repositories h2'",
     "     VISIBLE:  'Adding IPS Repositories h2', cursor=1",
     "SPEECH OUTPUT: 'Adding IPS Repositories heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "3. h",
    ["BRAILLE LINE:  'Other Repositories h3'",
     "     VISIBLE:  'Other Repositories h3', cursor=1",
     "SPEECH OUTPUT: 'Other Repositories heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "4. h",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'This is a test. h1'",
     "     VISIBLE:  'This is a test. h1', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'This is a test. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift h",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'Other Repositories h3'",
     "     VISIBLE:  'Other Repositories h3', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'Other Repositories heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "6. Shift h",
    ["BRAILLE LINE:  'Adding IPS Repositories h2'",
     "     VISIBLE:  'Adding IPS Repositories h2', cursor=1",
     "SPEECH OUTPUT: 'Adding IPS Repositories heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "7. Shift h",
    ["BRAILLE LINE:  'This is a test. h1'",
     "     VISIBLE:  'This is a test. h1', cursor=1",
     "SPEECH OUTPUT: 'This is a test. heading level 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
