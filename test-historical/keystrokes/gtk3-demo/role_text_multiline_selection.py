#!/usr/bin/python

"""Test of multiline editable text."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>a"))
sequence.append(utils.AssertPresentationAction(
    "1. Select all'",
    ["BRAILLE LINE:  'gtk3-demo application Hypertext frame Some text to show that simple hyper text can easily be realized with  $l'",
     "     VISIBLE:  'Some text to show that simple hy', cursor=1",
     "SPEECH OUTPUT: 'entire document selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete"))
sequence.append(utils.AssertPresentationAction(
    "2. Delete the selection",
    ["BRAILLE LINE:  'gtk3-demo application Hypertext frame  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Selection deleted.'",
     "     VISIBLE:  'Selection deleted.', cursor=0",
     "BRAILLE LINE:  'gtk3-demo application Hypertext frame  $l'",
     "     VISIBLE:  'frame  $l', cursor=7",
     "SPEECH OUTPUT: 'Selection deleted.' voice=system"]))

sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("This is another test."))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Select two words'",
    ["BRAILLE LINE:  'gtk3-demo application Hypertext frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=5",
     "BRAILLE LINE:  'gtk3-demo application Hypertext frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=8",
     "SPEECH OUTPUT: 'This'",
     "SPEECH OUTPUT: 'selected' voice=system",
     "SPEECH OUTPUT: ' is'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>c"))
sequence.append(utils.AssertPresentationAction(
    "4. Copy the selection",
    ["BRAILLE LINE:  'Copied selection to clipboard.'",
     "     VISIBLE:  'Copied selection to clipboard.', cursor=0",
     "SPEECH OUTPUT: 'Copied selection to clipboard.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "5. End of file",
    ["BRAILLE LINE:  'gtk3-demo application Hypertext frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=8",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'This is'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "6. Newline",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>v"))
sequence.append(utils.AssertPresentationAction(
    "7. Paste",
    ["BRAILLE LINE:  'This is $l'",
     "     VISIBLE:  'This is $l', cursor=8",
     "BRAILLE LINE:  'Pasted contents from clipboard.'",
     "     VISIBLE:  'Pasted contents from clipboard.', cursor=0",
     "BRAILLE LINE:  'This is $l'",
     "     VISIBLE:  'This is $l', cursor=8",
     "SPEECH OUTPUT: 'Pasted contents from clipboard.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Select Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: '",
     "This is'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Select Up",
    ["BRAILLE LINE:  'This is another test. $l'",
     "     VISIBLE:  'This is another test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is another test.",
     "'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>x"))
sequence.append(utils.AssertPresentationAction(
    "10. Cut the selection",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Cut selection to clipboard.'",
     "     VISIBLE:  'Cut selection to clipboard.', cursor=0",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Cut selection to clipboard.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>x"))
sequence.append(utils.AssertPresentationAction(
    "11. Cut with nothing selected",
    [""]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
