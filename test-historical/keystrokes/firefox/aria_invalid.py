#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab",
    ["BRAILLE LINE:  'text 1 Hello wurld $l spelling'",
     "     VISIBLE:  'text 1 Hello wurld $l spelling', cursor=19",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'text 1 entry Hello wurld selected.'",
     "SPEECH OUTPUT: 'invalid spelling'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. WhereAmI",
    ["BRAILLE LINE:  'text 1 Hello wurld $l spelling'",
     "     VISIBLE:  'text 1 Hello wurld $l spelling', cursor=19",
     "BRAILLE LINE:  'text 1 Hello wurld $l spelling'",
     "     VISIBLE:  'text 1 Hello wurld $l spelling', cursor=19",
     "SPEECH OUTPUT: 'text 1 entry Hello wurld selected.'",
     "SPEECH OUTPUT: 'invalid spelling'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'text 2 World hello $l grammar'",
     "     VISIBLE:  'text 2 World hello $l grammar', cursor=19",
     "SPEECH OUTPUT: 'text 2 entry World hello selected.'",
     "SPEECH OUTPUT: 'invalid grammar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. WhereAmI",
    ["BRAILLE LINE:  'text 2 World hello $l grammar'",
     "     VISIBLE:  'text 2 World hello $l grammar', cursor=19",
     "SPEECH OUTPUT: 'text 2 entry World hello selected.'",
     "SPEECH OUTPUT: 'invalid grammar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab",
    ["BRAILLE LINE:  'text 3 1234 $l invalid'",
     "     VISIBLE:  'text 3 1234 $l invalid', cursor=12",
     "SPEECH OUTPUT: 'text 3 entry 1234 selected.'",
     "SPEECH OUTPUT: 'invalid entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. WhereAmI",
    ["BRAILLE LINE:  'text 3 1234 $l invalid'",
     "     VISIBLE:  'text 3 1234 $l invalid', cursor=12",
     "SPEECH OUTPUT: 'text 3 entry 1234 selected.'",
     "SPEECH OUTPUT: 'invalid entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab",
    ["BRAILLE LINE:  'text 4 Good $l'",
     "     VISIBLE:  'text 4 Good $l', cursor=12",
     "SPEECH OUTPUT: 'text 4 entry Good selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. WhereAmI",
    ["BRAILLE LINE:  'text 4 Good $l'",
     "     VISIBLE:  'text 4 Good $l', cursor=12",
     "SPEECH OUTPUT: 'text 4 entry Good selected.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab",
    ["BRAILLE LINE:  '< > accept terms of service check box'",
     "     VISIBLE:  '< > accept terms of service chec', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'accept terms of service check box not checked.'",
     "SPEECH OUTPUT: 'invalid entry'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. WhereAmI",
    ["BRAILLE LINE:  '< > accept terms of service check box'",
     "     VISIBLE:  '< > accept terms of service chec', cursor=1",
     "BRAILLE LINE:  '< > accept terms of service check box'",
     "     VISIBLE:  '< > accept terms of service chec', cursor=1",
     "SPEECH OUTPUT: 'accept terms of service check box not checked.'",
     "SPEECH OUTPUT: 'invalid entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "11. Tab",
    ["BRAILLE LINE:  'time 1  $l'",
     "     VISIBLE:  'time 1  $l', cursor=8",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'time 1 entry.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "12. WhereAmI",
    ["BRAILLE LINE:  'time 1  $l'",
     "     VISIBLE:  'time 1  $l', cursor=8",
     "BRAILLE LINE:  'time 1  $l'",
     "     VISIBLE:  'time 1  $l', cursor=8",
     "SPEECH OUTPUT: 'time 1 entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "13. Tab",
    ["BRAILLE LINE:  'time 2 11:30 PM $l invalid'",
     "     VISIBLE:  'time 2 11:30 PM $l invalid', cursor=16",
     "SPEECH OUTPUT: 'time 2 entry 11:30 PM selected.'",
     "SPEECH OUTPUT: 'invalid entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "14. WhereAmI",
    ["BRAILLE LINE:  'time 2 11:30 PM $l invalid'",
     "     VISIBLE:  'time 2 11:30 PM $l invalid', cursor=16",
     "SPEECH OUTPUT: 'time 2 entry 11:30 PM selected.'",
     "SPEECH OUTPUT: 'invalid entry'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
