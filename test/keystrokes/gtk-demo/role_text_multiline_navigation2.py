#!/usr/bin/python

"""Test of text output for caret navigation and flat review."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

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
    "Shift+Ctrl+Page_Up to select text to beginning of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'line selected from start to previous cursor position'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Ctrl+Page_Down to select text to end of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'line selected to end from previous cursor position'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Up to deselect some text and select some text above",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=17",
     "SPEECH OUTPUT: 'is only a test.'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: '",
     "This '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Down to deselect some text and select some text below",
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
    "Ctrl+Page_Up to beginning of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'is only a test.'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Page_Down to end of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'This is only a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Page up",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Page down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Page_Up to select text",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'page selected to cursor position'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Page_Down to deselect text",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank' voice=system",
     "SPEECH OUTPUT: 'page unselected from cursor position'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Page_Up",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'This is a test. ",
     "'",
     "SPEECH OUTPUT: 'This is only a test.",
     "'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
