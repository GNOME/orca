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
    ["KNOWN ISSUE: We should not be speaking 'Jimmy Johns'",
     "BRAILLE LINE:  '&=y Radio Maria radio button'",
     "     VISIBLE:  '&=y Radio Maria radio button', cursor=1",
     "BRAILLE LINE:  '&=y Radio Maria radio button'",
     "     VISIBLE:  '&=y Radio Maria radio button', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options panel'",
     "SPEECH OUTPUT: 'Jimmy Johns Radio Maria selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereamI",
    ["KNOWN ISSUE: We should not be speaking 'Jimmy Johns'",
     "BRAILLE LINE:  '&=y Radio Maria radio button'",
     "     VISIBLE:  '&=y Radio Maria radio button', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options Jimmy Johns Radio Maria'",
     "SPEECH OUTPUT: 'radio button selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Move to next radio button",
    ["KNOWN ISSUE: It looks like at the time we move to it, the state hasn't changed yet. This is something better handled by focus mode but users don't want that.",
     "BRAILLE LINE:  '& y Rainbow Gardens radio button'",
     "     VISIBLE:  '& y Rainbow Gardens radio button', cursor=1",
     "SPEECH OUTPUT: 'Rainbow Gardens'",
     "SPEECH OUTPUT: 'not selected'",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Basic whereamI",
    ["KNOWN ISSUE: We should not be speaking 'Radio Maria'",
     "BRAILLE LINE:  '&=y Rainbow Gardens radio button'",
     "     VISIBLE:  '&=y Rainbow Gardens radio button', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options Radio Maria Rainbow Gardens'",
     "SPEECH OUTPUT: 'radio button selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Move to next line",
    ["BRAILLE LINE:  'Drink Options h3'",
     "     VISIBLE:  'Drink Options h3', cursor=1",
     "SPEECH OUTPUT: 'Drink Options'",
     "SPEECH OUTPUT: 'heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to second radio group",
    ["BRAILLE LINE:  '&=y Water radio button'",
     "     VISIBLE:  '&=y Water radio button', cursor=1",
     "BRAILLE LINE:  '&=y Water radio button'",
     "     VISIBLE:  '&=y Water radio button', cursor=1",
     "SPEECH OUTPUT: 'Drink Options panel'",
     "SPEECH OUTPUT: 'Water selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Move to next radio button",
    ["KNOWN ISSUE: It looks like at the time we move to it, the state hasn't changed yet. This is something better handled by focus mode but users don't want that.",
     "BRAILLE LINE:  '& y Tea radio button'",
     "     VISIBLE:  '& y Tea radio button', cursor=1",
     "SPEECH OUTPUT: 'Tea'",
     "SPEECH OUTPUT: 'not selected'",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Move back to previous radio button",
    ["KNOWN ISSUE: It looks like at the time we move to it, the state hasn't changed yet. This is something better handled by focus mode but users don't want that.",
     "BRAILLE LINE:  '& y Water radio button'",
     "     VISIBLE:  '& y Water radio button', cursor=1",
     "SPEECH OUTPUT: 'Water'",
     "SPEECH OUTPUT: 'not selected'",
     "SPEECH OUTPUT: 'radio button'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
