#!/usr/bin/python

"""Test of document tabs"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(15000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>2"))
sequence.append(utils.AssertPresentationAction(
    "1. Switch to second page tab - Orca wiki",
    ["KNOWN ISSUE: We are not presenting the page tab",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>1"))
sequence.append(utils.AssertPresentationAction(
    "2. Switch to first page tab - Test page",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'document frame blank'"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>3"))
sequence.append(utils.AssertPresentationAction(
    "3. Switch to third page tab - Bugzilla",
    ["BRAILLE LINE:  'Enter a bug # or some search terms:  $l'",
     "     VISIBLE:  ' a bug # or some search terms:  ', cursor=32",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Enter a bug # or some search terms: entry'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Ctrl>w"))
sequence.append(utils.AssertPresentationAction(
    "4. Close third page tab - land in second page",
    ["KNOWN ISSUE: EOCs",
     "BRAILLE LINE:  '\ufffc\ufffc'",
     "     VISIBLE:  '\ufffc\ufffc', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'document frame'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
