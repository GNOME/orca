#!/usr/bin/python

"""Test of HTML links presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Here are some of our local test files:'",
     "     VISIBLE:  'Here are some of our local test ', cursor=1",
     "SPEECH OUTPUT: 'Here are some of our local test files:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to anchors.html link",
    ["BRAILLE LINE:  'anchors.html'",
     "     VISIBLE:  'anchors.html', cursor=1",
     "SPEECH OUTPUT: 'anchors.html link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to blockquotes.html link",
    ["BRAILLE LINE:  'blockquotes.html'",
     "     VISIBLE:  'blockquotes.html', cursor=1",
     "SPEECH OUTPUT: 'blockquotes.html link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to bugzilla_top.html link",
    ["BRAILLE LINE:  'bugzilla_top.html'",
     "     VISIBLE:  'bugzilla_top.html', cursor=1",
     "SPEECH OUTPUT: 'bugzilla_top.html link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift Tab to blockquotes.html link",
    ["BRAILLE LINE:  'blockquotes.html'",
     "     VISIBLE:  'blockquotes.html', cursor=1",
     "SPEECH OUTPUT: 'blockquotes.html link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Basic Where Am I",
    ["BRAILLE LINE:  'blockquotes.html'",
     "     VISIBLE:  'blockquotes.html', cursor=1",
     "SPEECH OUTPUT: 'file link to blockquotes.html.'",
     "SPEECH OUTPUT: 'same site.'",
     "SPEECH OUTPUT: '1235 bytes.'"]))

sequence.append(KeyComboAction("Return"))
#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(KeyComboAction("<Alt>Left"))
#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up to anchors.html",
    ["BRAILLE LINE:  '• anchors.html'",
     "     VISIBLE:  '• anchors.html', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'anchors.html'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
