#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("So is this line."))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>a"))
sequence.append(utils.AssertPresentationAction(
    "1. Select all'",
    ["BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7",
     "SPEECH OUTPUT: 'entire document selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete"))
sequence.append(utils.AssertPresentationAction(
    "2. Delete the selection",
    ["BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7",
     "BRAILLE LINE:  'Selection deleted.'",
     "     VISIBLE:  'Selection deleted.', cursor=0",
     "SPEECH OUTPUT: 'Selection deleted.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>z"))
sequence.append(utils.AssertPresentationAction(
    "3. Undo",
    ["BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7",
     "BRAILLE LINE:  'undo'",
     "     VISIBLE:  'undo', cursor=0",
     "BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7",
     "BRAILLE LINE:  'Selection restored.'",
     "     VISIBLE:  'Selection restored.', cursor=0",
     "BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7",
     "SPEECH OUTPUT: 'undo' voice=system",
     "SPEECH OUTPUT: 'Selection restored.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up'",
    ["BRAILLE LINE:  'Label This is a test. $l'",
     "     VISIBLE:  'Label This is a test. $l', cursor=7",
     "BRAILLE LINE:  'Label This is a test. $l'",
     "     VISIBLE:  'Label This is a test. $l', cursor=7",
     "SPEECH OUTPUT: 'This is a test.",
     "So is this line.",
     "'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Press Up and select two words'",
    ["BRAILLE LINE:  'Label This is a test. $l'",
     "     VISIBLE:  'Label This is a test. $l', cursor=11",
     "BRAILLE LINE:  'Label This is a test. $l'",
     "     VISIBLE:  'Label This is a test. $l', cursor=14",
     "SPEECH OUTPUT: 'This'",
     "SPEECH OUTPUT: 'selected' voice=system",
     "SPEECH OUTPUT: ' is'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>c"))
sequence.append(utils.AssertPresentationAction(
    "6. Copy the selection",
    ["BRAILLE LINE:  'Copied selection to clipboard.'",
     "     VISIBLE:  'Copied selection to clipboard.', cursor=0",
     "SPEECH OUTPUT: 'Copied selection to clipboard.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "7. End of file",
    ["BRAILLE LINE:  'Label This is a test. $l'",
     "     VISIBLE:  'Label This is a test. $l', cursor=14",
     "SPEECH OUTPUT: 'This is'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "8. Newline",
    ["BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7",
     "BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>v"))
sequence.append(utils.AssertPresentationAction(
    "9. Paste",
    ["BRAILLE LINE:  'Label This is $l'",
     "     VISIBLE:  'Label This is $l', cursor=14",
     "BRAILLE LINE:  'Pasted contents from clipboard.'",
     "     VISIBLE:  'Pasted contents from clipboard.', cursor=0",
     "BRAILLE LINE:  'Label This is $l'",
     "     VISIBLE:  'Label This is $l', cursor=14",
     "SPEECH OUTPUT: 'Pasted contents from clipboard.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Select Up",
    ["BRAILLE LINE:  'Label  $l'",
     "     VISIBLE:  'Label  $l', cursor=7",
     "SPEECH OUTPUT: '",
     "This is'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Select Up",
    ["BRAILLE LINE:  'Label So is this line. $l'",
     "     VISIBLE:  'Label So is this line. $l', cursor=14",
     "SPEECH OUTPUT: 'his line.",
     "'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>x"))
sequence.append(utils.AssertPresentationAction(
    "12. Cut the selection",
    ["BRAILLE LINE:  'Label So is t $l'",
     "     VISIBLE:  'Label So is t $l', cursor=14",
     "BRAILLE LINE:  'Cut selection to clipboard.'",
     "     VISIBLE:  'Cut selection to clipboard.', cursor=0",
     "SPEECH OUTPUT: 'Cut selection to clipboard.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>x"))
sequence.append(utils.AssertPresentationAction(
    "13. Cut with nothing selected",
    ["BRAILLE LINE:  'Label So is t $l'",
     "     VISIBLE:  'Label So is t $l', cursor=14"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
