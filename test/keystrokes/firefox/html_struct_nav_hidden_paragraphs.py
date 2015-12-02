#!/usr/bin/python

"""Test of structural navigation by paragraph with some paragraphs hidden."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This element is not hidden.'",
     "     VISIBLE:  'This element is not hidden.', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "2. p to next paragraph",
    ["BRAILLE LINE:  'This element hidden by position off screen.'",
     "     VISIBLE:  'This element hidden by position ', cursor=1",
     "SPEECH OUTPUT: 'This element hidden by position off screen.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "3. p to next paragraph",
    ["BRAILLE LINE:  'This element is in a parent which is not hidden.'",
     "     VISIBLE:  'This element is in a parent whic', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent which is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "4. p to next paragraph",
    ["BRAILLE LINE:  'This element is in a parent hidden by position off screen'",
     "     VISIBLE:  'This element is in a parent hidd', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent hidden by position off screen'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift p to previous paragraph",
    ["BRAILLE LINE:  'This element is in a parent which is not hidden.'",
     "     VISIBLE:  'This element is in a parent whic', cursor=1",
     "SPEECH OUTPUT: 'This element is in a parent which is not hidden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "6. Shift p to previous paragraph",
    ["BRAILLE LINE:  'This element hidden by position off screen.'",
     "     VISIBLE:  'This element hidden by position ', cursor=1",
     "SPEECH OUTPUT: 'This element hidden by position off screen.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "7. Shift p to previous paragraph",
    ["BRAILLE LINE:  'This element is not hidden.'",
     "     VISIBLE:  'This element is not hidden.', cursor=1",
     "SPEECH OUTPUT: 'This element is not hidden.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
