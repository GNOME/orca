#!/usr/bin/python

"""Test of multiline editable text."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(TypeAction("This is a tes"))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("t."))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Typing",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test $l'",
     "     VISIBLE:  'frame This is a test $l', cursor=21",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test $l'",
     "     VISIBLE:  'frame This is a test $l', cursor=21",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'frame This is a test. $l', cursor=22",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'frame This is a test. $l', cursor=22",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1"]))

sequence.append(TypeAction("Here is another test."))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "2. Navigate home",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Arrow to end of 'This'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=2",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=3",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=4",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=5",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Select 'is a test'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=8",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=10",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: ' is'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: ' a'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: ' test'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Unselect 'test'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'text.'",
     "SPEECH OUTPUT: ' is a  selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Shift Down",
    ["BRAILLE LINE:  'Here is another test. $l'",
     "     VISIBLE:  'Here is another test. $l', cursor=10",
     "SPEECH OUTPUT: 'test.",
     "Here is a'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>End"))
sequence.append(utils.AssertPresentationAction(
    "8. Shift End",
    ["BRAILLE LINE:  'Here is another test. $l'",
     "     VISIBLE:  'Here is another test. $l', cursor=22",
     "SPEECH OUTPUT: 'nother test.'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "9. Basic Where Am I multiline selection",
    ["BRAILLE LINE:  'Here is another test. $l'",
     "     VISIBLE:  'Here is another test. $l', cursor=22",
     "SPEECH OUTPUT: 'text.'",
     "SPEECH OUTPUT: ' is a test.",
     "Here is another test. selected.'"]))

sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Detailed Where Am I multiline selection",
    ["BRAILLE LINE:  'Here is another test. $l'",
     "     VISIBLE:  'Here is another test. $l', cursor=22",
     "SPEECH OUTPUT: 'text.'",
     "SPEECH OUTPUT: ' is a test.",
     "Here is another test. selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "11. Navigate home",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=1",
     "SPEECH OUTPUT: ' is a test.",
     "Here is another test.'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "12. SayAll",
    ["SPEECH OUTPUT: 'This is a test.",
     "'",
     "SPEECH OUTPUT: 'Here is another test.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
