#!/usr/bin/python

"""Test of UIUC button presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first button",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button &=y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Font Larger toggle button & ', cursor=1",
     "BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button &=y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Font Larger toggle button & ', cursor=1",
     "SPEECH OUTPUT: 'Font Larger'",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereamI",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button &=y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Font Larger toggle button & ', cursor=1",
     "SPEECH OUTPUT: 'Font Larger'",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to second button",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button &=y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Font Smaller toggle button &', cursor=1",
     "BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button &=y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Font Smaller toggle button &', cursor=1",
     "SPEECH OUTPUT: 'Font Smaller'",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "4. Push second button",
    ["KNOWN ISSUE: We are presenting nothing here for some reason. Missing event?",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to third button",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button &=y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '&=y Italic toggle button & y Bol', cursor=1",
     "BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button &=y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '&=y Italic toggle button & y Bol', cursor=1",
     "SPEECH OUTPUT: 'Italic'",
     "SPEECH OUTPUT: 'toggle button pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "6. Push third button",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button & y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Italic toggle button & y Bol', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab to fourth button",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button & y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Bold toggle button', cursor=1",
     "BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button & y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'Bold'",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "8. Push fourth button",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button & y Italic toggle button &=y Bold toggle button'",
     "     VISIBLE:  '&=y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "9. Push fourth button again",
    ["BRAILLE LINE:  '& y Font Larger toggle button & y Font Smaller toggle button & y Italic toggle button & y Bold toggle button'",
     "     VISIBLE:  '& y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
