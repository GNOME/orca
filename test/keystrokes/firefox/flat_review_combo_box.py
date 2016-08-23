#!/usr/bin/python

"""Test of flat reviewing HTML."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Flat review current line",
    ["BRAILLE LINE:  'Severity normal combo box'",
     "     VISIBLE:  'Severity normal combo box', cursor=10",
     "BRAILLE LINE:  'Severity Severity :  normal $l'",
     "     VISIBLE:  'Severity Severity :  normal $l', cursor=22",
     "SPEECH OUTPUT: 'Severity Severity :  normal'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "2. Flat review next line",
    ["BRAILLE LINE:  'Priority :  Normal $l'",
     "     VISIBLE:  'Priority :  Normal $l', cursor=1",
     "SPEECH OUTPUT: 'Priority :  Normal'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "3. Flat review next line",
    ["BRAILLE LINE:  'Resolution:  $l'",
     "     VISIBLE:  'Resolution:  $l', cursor=1",
     "SPEECH OUTPUT: 'Resolution: ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Flat review next line",
    ["BRAILLE LINE:  'FIXED $l'",
     "     VISIBLE:  'FIXED $l', cursor=1",
     "SPEECH OUTPUT: 'FIXED'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "5. Flat review next line",
    ["BRAILLE LINE:  'Version 2.16 $l'",
     "     VISIBLE:  'Version 2.16 $l', cursor=1",
     "SPEECH OUTPUT: 'Version 2.16'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Flat review next line",
    ["BRAILLE LINE:  'Component $l'",
     "     VISIBLE:  'Component $l', cursor=1",
     "SPEECH OUTPUT: 'Component'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Flat review next line",
    ["BRAILLE LINE:  'Speech $l'",
     "     VISIBLE:  'Speech $l', cursor=1",
     "SPEECH OUTPUT: 'Speech'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
