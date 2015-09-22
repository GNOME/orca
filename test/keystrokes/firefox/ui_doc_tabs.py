#!/usr/bin/python

"""Test of document tabs"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(WaitForDocLoad())

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>2"))
sequence.append(utils.AssertPresentationAction(
    "1. Switch to second page tab - Orca wiki",
    ["BRAILLE LINE:  'Firefox application Orca - GNOME Live! - (Mozilla Firefox|Nightly) frame Browser tabs tool bar Orca - GNOME Live! page tab'",
     "     VISIBLE:  'Orca - GNOME Live! page tab', cursor=1",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'Orca - GNOME Live! page tab.'",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>1"))
sequence.append(utils.AssertPresentationAction(
    "2. Switch to first page tab - Test page",
    ["BRAILLE LINE:  'Firefox application HTML test page - (Mozilla Firefox|Nightly) frame Browser tabs tool bar HTML test page page tab'",
     "     VISIBLE:  'HTML test page page tab', cursor=1",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'HTML test page page tab.'",
     "SPEECH OUTPUT: 'document frame blank'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>3"))
sequence.append(utils.AssertPresentationAction(
    "3. Switch to third page tab - Bugzilla",
    ["BRAILLE LINE:  'Firefox application GNOME Bug Tracking System - (Mozilla Firefox|Nightly) frame Browser tabs tool bar GNOME Bug Tracking System page tab'",
     "     VISIBLE:  'GNOME Bug Tracking System page t', cursor=1",
     "BRAILLE LINE:  'Enter a bug # or some search terms:  $l'",
     "     VISIBLE:  ' a bug # or some search terms:  ', cursor=32",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'GNOME Bug Tracking System page tab.'",
     "SPEECH OUTPUT: 'Enter a bug # or some search terms: entry'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Ctrl>w"))
sequence.append(utils.AssertPresentationAction(
    "4. Close third page tab - land in second page",
    ["BRAILLE LINE:  'Firefox application Orca - GNOME Live! - (Mozilla Firefox|Nightly) frame Browser tabs tool bar Orca - GNOME Live! page tab'",
     "     VISIBLE:  'Orca - GNOME Live! page tab', cursor=1",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'Orca - GNOME Live! page tab.'",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
