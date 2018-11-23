#!/usr/bin/python

"""Test of structural navigation by heading."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("2"))
sequence.append(utils.AssertPresentationAction(
    "1. 2 for first Heading",
    ["BRAILLE LINE:  'First Heading  h2'",
     "     VISIBLE:  'First Heading  h2', cursor=1",
     "SPEECH OUTPUT: 'First Heading'",
     "SPEECH OUTPUT: 'link heading level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow to text after First Heading",
    ["BRAILLE LINE:  'text'",
     "     VISIBLE:  'text', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("2"))
sequence.append(utils.AssertPresentationAction(
    "3. 2 to move to the next heading",
    ["BRAILLE LINE:  'Second Heading  h2'",
     "     VISIBLE:  'Second Heading  h2', cursor=1",
     "SPEECH OUTPUT: 'Second Heading'",
     "SPEECH OUTPUT: 'link heading level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow to text after First Heading",
    ["BRAILLE LINE:  'text'",
     "     VISIBLE:  'text', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>2"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift+2 to move to the previous heading",
    ["BRAILLE LINE:  'Second Heading  h2'",
     "     VISIBLE:  'Second Heading  h2', cursor=1",
     "SPEECH OUTPUT: 'Second Heading'",
     "SPEECH OUTPUT: 'link heading level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up Arrow to text after First Heading",
    ["BRAILLE LINE:  'text'",
     "     VISIBLE:  'text', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>2"))
sequence.append(utils.AssertPresentationAction(
    "7. Shift+2 to move to the previous heading",
    ["BRAILLE LINE:  'First Heading  h2'",
     "     VISIBLE:  'First Heading  h2', cursor=1",
     "SPEECH OUTPUT: 'First Heading'",
     "SPEECH OUTPUT: 'link heading level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>2"))
sequence.append(utils.AssertPresentationAction(
    "8. Shift+2 to move to the previous heading",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'Second Heading  h2'",
     "     VISIBLE:  'Second Heading  h2', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'Second Heading'",
     "SPEECH OUTPUT: 'link heading level 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("2"))
sequence.append(utils.AssertPresentationAction(
    "9. 2 to move to the next heading",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'First Heading  h2'",
     "     VISIBLE:  'First Heading  h2', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'First Heading'",
     "SPEECH OUTPUT: 'link heading level 2.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
