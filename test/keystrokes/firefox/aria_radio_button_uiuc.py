#!/usr/bin/python

"""Test of UIUC radio button presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first radio button",
    ["KNOWN ISSUE: This is broken. So are the tests which follow.",
     "BRAILLE LINE:  ' Radio'",
     "     VISIBLE:  ' Radio', cursor=1",
     "BRAILLE LINE:  ' Radio'",
     "     VISIBLE:  ' Radio', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options panel'",
     "SPEECH OUTPUT: 'Johns Radio Maria selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereamI",
    ["BRAILLE LINE:  ' Radio'",
     "     VISIBLE:  ' Radio', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options Johns Radio Maria'",
     "SPEECH OUTPUT: 'radio button selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Move to next radio button",
    ["BRAILLE LINE:  'Maria'",
     "     VISIBLE:  'Maria', cursor=1",
     "SPEECH OUTPUT: 'Maria '",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Move to next radio button",
    ["BRAILLE LINE:  ' Rainbow'",
     "     VISIBLE:  ' Rainbow', cursor=1",
     "SPEECH OUTPUT: ' Rainbow '",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Move to next radio button",
    ["BRAILLE LINE:  'Gardens'",
     "     VISIBLE:  'Gardens', cursor=1",
     "SPEECH OUTPUT: 'Gardens '",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Move to next line",
    ["BRAILLE LINE:  'Drink Options h3'",
     "     VISIBLE:  'Drink Options h3', cursor=1",
     "SPEECH OUTPUT: 'Drink Options'",
     "SPEECH OUTPUT: 'heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab to second radio group",
    ["BRAILLE LINE:  ' Water'",
     "     VISIBLE:  ' Water', cursor=1",
     "BRAILLE LINE:  ' Water'",
     "     VISIBLE:  ' Water', cursor=1",
     "SPEECH OUTPUT: 'Drink Options panel'",
     "SPEECH OUTPUT: 'Water selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Move to next radio button",
    ["BRAILLE LINE:  ' Tea'",
     "     VISIBLE:  ' Tea', cursor=1",
     "SPEECH OUTPUT: ' Tea '",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Move back to previous radio button",
    ["BRAILLE LINE:  ' Water'",
     "     VISIBLE:  ' Water', cursor=1",
     "SPEECH OUTPUT: ' Water '",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
