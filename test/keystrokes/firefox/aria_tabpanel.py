#!/usr/bin/python

"""Test of ARIA tabpanel presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Basic whereAmI",
    ["BRAILLE LINE:  'Tab Zero page tab'",
     "     VISIBLE:  'Tab Zero page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list'",
     "SPEECH OUTPUT: 'Tab Zero'",
     "SPEECH OUTPUT: 'page tab 1 of 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right arrow to next tab",
    ["BRAILLE LINE:  'Tab One page tab'",
     "     VISIBLE:  'Tab One page tab', cursor=1",
     "BRAILLE LINE:  'Tab One page tab'",
     "     VISIBLE:  'Tab One page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab One page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right arrow to next tab",
    ["BRAILLE LINE:  'Tab Two page tab'",
     "     VISIBLE:  'Tab Two page tab', cursor=1",
     "BRAILLE LINE:  'Tab Two page tab'",
     "     VISIBLE:  'Tab Two page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab Two page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to contents",
    ["BRAILLE LINE:  '&=y Internal Portal Bookmark radio button'",
     "     VISIBLE:  '&=y Internal Portal Bookmark rad', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Internal Portal Bookmark selected radio button'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift+Tab out of contents",
    ["BRAILLE LINE:  '&=y Internal Portal Bookmark radio button'",
     "     VISIBLE:  '&=y Internal Portal Bookmark rad', cursor=1",
     "BRAILLE LINE:  'Tab Zero page tab Tab One page tab Tab Two page tab Tab Three page tab Tab Four page tab'",
     "     VISIBLE:  'Tab Two page tab Tab Three page ', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'Tab Two page tab'",
     "     VISIBLE:  'Tab Two page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab Two page tab'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Right arrow to next tab",
    ["BRAILLE LINE:  'Tab Three page tab'",
     "     VISIBLE:  'Tab Three page tab', cursor=1",
     "BRAILLE LINE:  'Tab Three page tab'",
     "     VISIBLE:  'Tab Three page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab Three page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "7. Right arrow to next tab",
    ["BRAILLE LINE:  'Tab Four page tab'",
     "     VISIBLE:  'Tab Four page tab', cursor=1",
     "BRAILLE LINE:  'Tab Four page tab'",
     "     VISIBLE:  'Tab Four page tab', cursor=1",
     "SPEECH OUTPUT: 'Tab Four page tab'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
