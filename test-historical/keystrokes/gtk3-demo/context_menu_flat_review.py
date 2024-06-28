#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))

sequence.append(KeyComboAction("<Shift>F10"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line",
    ["BRAILLE LINE:  'Cut $l'",
     "     VISIBLE:  'Cut $l', cursor=1",
     "SPEECH OUTPUT: 'Cut'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "2. Review previous line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "3. Review next line",
    ["BRAILLE LINE:  'Copy $l'",
     "     VISIBLE:  'Copy $l', cursor=1",
     "SPEECH OUTPUT: 'Copy'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  'Paste $l'",
     "     VISIBLE:  'Paste $l', cursor=1",
     "SPEECH OUTPUT: 'Paste'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "5. Review next line",
    ["BRAILLE LINE:  'Delete $l'",
     "     VISIBLE:  'Delete $l', cursor=1",
     "SPEECH OUTPUT: 'Delete'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  'separator $l'",
     "     VISIBLE:  'separator $l', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line",
    ["BRAILLE LINE:  'Select All $l'",
     "     VISIBLE:  'Select All $l', cursor=1",
     "SPEECH OUTPUT: 'Select All'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next line",
    ["BRAILLE LINE:  'Insert Emoji $l'",
     "     VISIBLE:  'Insert Emoji $l', cursor=1",
     "SPEECH OUTPUT: 'Insert Emoji'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
