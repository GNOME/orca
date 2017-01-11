#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Bypass mode",
    ["BRAILLE LINE:  'Bypass mode enabled.'",
     "     VISIBLE:  'Bypass mode enabled.', cursor=0",
     "SPEECH OUTPUT: 'Bypass mode enabled.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>1"))
sequence.append(utils.AssertPresentationAction(
    "3. Access key 1",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "BRAILLE LINE:  'accesskeys'",
     "     VISIBLE:  'accesskeys', cursor=1",
     "BRAILLE LINE:  'Form! h1'",
     "     VISIBLE:  'Form! h1', cursor=1",
     "SPEECH OUTPUT: 'accesskeys link.'",
     "SPEECH OUTPUT: 'Form! heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Bypass mode",
    ["BRAILLE LINE:  'Bypass mode enabled.'",
     "     VISIBLE:  'Bypass mode enabled.', cursor=0",
     "SPEECH OUTPUT: 'Bypass mode enabled.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>2"))
sequence.append(utils.AssertPresentationAction(
    "5. Access key 2",
    ["BRAILLE LINE:  'Form! h1'",
     "     VISIBLE:  'Form! h1', cursor=1",
     "BRAILLE LINE:  'Search:  $l I feel frightened push button'",
     "     VISIBLE:  'Search:  $l I feel frightened pu', cursor=9",
     "SPEECH OUTPUT: 'Search: entry.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
