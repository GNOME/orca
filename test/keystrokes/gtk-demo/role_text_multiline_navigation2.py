#!/usr/bin/python

"""Test of text output for caret navigation and flat review."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("This is a test. "))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("This is only a test."))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift+Ctrl+Page_Up to select text to beginning of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'line selected from start to previous cursor position' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Shift+Ctrl+Page_Down to select text to end of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'line selected to end from previous cursor position'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Shift+Up to deselect some text and select some text above",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=17",
     "SPEECH OUTPUT: 'is only a test.'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: '",
     "This '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Shift+Down to deselect some text and select some text below",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: '",
     "This '",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'is only a test.'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Ctrl+Page_Up to beginning of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'is only a test.'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Ctrl+Page_Down to end of line",
    ["KNOWN ISSUE: We're not saying anything here",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Page up",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Page down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Shift+Page_Up to select text",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'page selected to cursor position'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Shift+Page_Down to deselect text",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'page unselected from cursor position' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Page_Up",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "12. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'This is a test. ",
     "'",
     "SPEECH OUTPUT: 'This is only a test.",
     "'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
