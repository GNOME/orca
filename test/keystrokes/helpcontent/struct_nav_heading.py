#!/usr/bin/python

"""Test of learn mode."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(KeyComboAction("F1"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "1. h for next heading",
    ["BRAILLE LINE:  ' Before You Begin h2'",
     "     VISIBLE:  ' Before You Begin h2', cursor=2",
     "BRAILLE LINE:  ' Before You Begin h2'",
     "     VISIBLE:  ' Before You Begin h2', cursor=2",
     "SPEECH OUTPUT: 'Before You Begin heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "2. h for next heading",
    ["BRAILLE LINE:  ' Getting Started h2'",
     "     VISIBLE:  ' Getting Started h2', cursor=2",
     "BRAILLE LINE:  ' Getting Started h2'",
     "     VISIBLE:  ' Getting Started h2', cursor=2",
     "SPEECH OUTPUT: 'Getting Started heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "3. h for next heading",
    ["BRAILLE LINE:  ' Reading Documents and Web Pages h2'",
     "     VISIBLE:  'Reading Documents and Web Pages ', cursor=1",
     "BRAILLE LINE:  ' Reading Documents and Web Pages h2'",
     "     VISIBLE:  'Reading Documents and Web Pages ', cursor=1",
     "SPEECH OUTPUT: 'Reading Documents and Web Pages heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "4. h for next heading",
    ["BRAILLE LINE:  ' Reviewing and Interacting with Screen Contents h2'",
     "     VISIBLE:  'Reviewing and Interacting with S', cursor=1",
     "BRAILLE LINE:  ' Reviewing and Interacting with Screen Contents h2'",
     "     VISIBLE:  'Reviewing and Interacting with S', cursor=1",
     "SPEECH OUTPUT: 'Reviewing and Interacting with Screen Contents heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "5. h for next heading",
    ["BRAILLE LINE:  ' Quick Reference h2'",
     "     VISIBLE:  ' Quick Reference h2', cursor=2",
     "BRAILLE LINE:  ' Quick Reference h2'",
     "     VISIBLE:  ' Quick Reference h2', cursor=2",
     "SPEECH OUTPUT: 'Quick Reference heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "6. h for next heading",
    ["BRAILLE LINE:  ' About h2'",
     "     VISIBLE:  ' About h2', cursor=2",
     "BRAILLE LINE:  ' About h2'",
     "     VISIBLE:  ' About h2', cursor=2",
     "SPEECH OUTPUT: 'About heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "7. h for next heading",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  ' Orca's logo Orca Screen Reader h1'",
     "     VISIBLE:  'Orca's logo Orca Screen Reader h', cursor=1",
     "BRAILLE LINE:  ' Orca's logo Orca Screen Reader h1'",
     "     VISIBLE:  'Orca's logo Orca Screen Reader h', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'Orca's logo Orca Screen Reader heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "10. shift+h for previous heading",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  ' About h2'",
     "     VISIBLE:  ' About h2', cursor=2",
     "BRAILLE LINE:  ' About h2'",
     "     VISIBLE:  ' About h2', cursor=2",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'About heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "11. shift+h for previous heading",
    ["BRAILLE LINE:  ' Quick Reference h2'",
     "     VISIBLE:  ' Quick Reference h2', cursor=2",
     "BRAILLE LINE:  ' Quick Reference h2'",
     "     VISIBLE:  ' Quick Reference h2', cursor=2",
     "SPEECH OUTPUT: 'Quick Reference heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "12. shift+h for previous heading",
    ["BRAILLE LINE:  ' Reviewing and Interacting with Screen Contents h2'",
     "     VISIBLE:  'Reviewing and Interacting with S', cursor=1",
     "BRAILLE LINE:  ' Reviewing and Interacting with Screen Contents h2'",
     "     VISIBLE:  'Reviewing and Interacting with S', cursor=1",
     "SPEECH OUTPUT: 'Reviewing and Interacting with Screen Contents heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "13. shift+h for previous heading",
    ["BRAILLE LINE:  ' Reading Documents and Web Pages h2'",
     "     VISIBLE:  'Reading Documents and Web Pages ', cursor=1",
     "BRAILLE LINE:  ' Reading Documents and Web Pages h2'",
     "     VISIBLE:  'Reading Documents and Web Pages ', cursor=1",
     "SPEECH OUTPUT: 'Reading Documents and Web Pages heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "14. shift+h for previous heading",
    ["BRAILLE LINE:  ' Getting Started h2'",
     "     VISIBLE:  ' Getting Started h2', cursor=2",
     "BRAILLE LINE:  ' Getting Started h2'",
     "     VISIBLE:  ' Getting Started h2', cursor=2",
     "SPEECH OUTPUT: 'Getting Started heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "15. shift+h for previous heading",
    ["BRAILLE LINE:  ' Before You Begin h2'",
     "     VISIBLE:  ' Before You Begin h2', cursor=2",
     "BRAILLE LINE:  ' Before You Begin h2'",
     "     VISIBLE:  ' Before You Begin h2', cursor=2",
     "SPEECH OUTPUT: 'Before You Begin heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "16. shift+h for previous heading",
    ["BRAILLE LINE:  ' Orca's logo Orca Screen Reader h1'",
     "     VISIBLE:  'Orca's logo Orca Screen Reader h', cursor=1",
     "BRAILLE LINE:  ' Orca's logo Orca Screen Reader h1'",
     "     VISIBLE:  'Orca's logo Orca Screen Reader h', cursor=1",
     "SPEECH OUTPUT: 'Orca's logo Orca Screen Reader heading level 1'"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
