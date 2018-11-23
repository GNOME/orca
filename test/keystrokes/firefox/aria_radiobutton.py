#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first radio button",
    ["BRAILLE LINE:  '&=y Radio Maria radio button'",
     "     VISIBLE:  '&=y Radio Maria radio button', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Lunch Options panel.'",
     "SPEECH OUTPUT: 'Radio Maria.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereamI",
    ["BRAILLE LINE:  '&=y Radio Maria radio button'",
     "     VISIBLE:  '&=y Radio Maria radio button', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options.'",
     "SPEECH OUTPUT: 'Radio Maria radio button.'",
     "SPEECH OUTPUT: 'selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Move to next radio button",
    ["BRAILLE LINE:  '&=y Rainbow Gardens radio button'",
     "     VISIBLE:  '&=y Rainbow Gardens radio button', cursor=1",
     "SPEECH OUTPUT: 'Rainbow Gardens.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Basic whereamI",
    ["BRAILLE LINE:  '&=y Rainbow Gardens radio button'",
     "     VISIBLE:  '&=y Rainbow Gardens radio button', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options.'",
     "SPEECH OUTPUT: 'Rainbow Gardens radio button.'",
     "SPEECH OUTPUT: 'selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down arrow within radio group",
    ["BRAILLE LINE:  '&=y Thai radio button'",
     "     VISIBLE:  '&=y Thai radio button', cursor=1",
     "SPEECH OUTPUT: 'Thai.'",
     "SPEECH OUTPUT: 'selected radio button'"]

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to second radio group",
    ["BRAILLE LINE:  '&=y Water radio button'",
     "     VISIBLE:  '&=y Water radio button', cursor=1",
     "SPEECH OUTPUT: 'leaving panel.'",
     "SPEECH OUTPUT: 'Drink Options panel.'",
     "SPEECH OUTPUT: 'Water.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Move to next radio button",
    ["BRAILLE LINE:  '&=y Tea radio button'",
     "     VISIBLE:  '&=y Tea radio button', cursor=1",
     "SPEECH OUTPUT: 'Tea.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Move back to previous radio button",
    ["BRAILLE LINE:  '&=y Water radio button'",
     "     VISIBLE:  '&=y Water radio button', cursor=1",
     "SPEECH OUTPUT: 'Water.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
