#!/usr/bin/python

"""Test of document tabs"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(10000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>2"))
sequence.append(utils.AssertPresentationAction(
    "1. Switch to second page tab - Orca wiki",
    ["BRAILLE LINE:  'Firefox application Orca - GNOME Live! - Firefox Nightly frame Browser tabs tool bar Orca - GNOME Live! page tab'",
     "     VISIBLE:  'Orca - GNOME Live! page tab', cursor=1",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'Orca - GNOME Live! page tab.'",
     "SPEECH OUTPUT: 'document web'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>1"))
sequence.append(utils.AssertPresentationAction(
    "2. Switch to first page tab - Test page",
    ["BRAILLE LINE:  'Firefox application HTML test page - Firefox Nightly frame Browser tabs tool bar HTML test page page tab'",
     "     VISIBLE:  'HTML test page page tab', cursor=1",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'HTML test page page tab.'",
     "SPEECH OUTPUT: 'document web blank'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>3"))
sequence.append(utils.AssertPresentationAction(
    "3. Switch to third page tab - Bugzilla",
    ["BRAILLE LINE:  'Firefox application GNOME Bug Tracking System - Firefox Nightly frame Browser tabs tool bar GNOME Bug Tracking System page tab'",
     "     VISIBLE:  'GNOME Bug Tracking System page t', cursor=1",
     "BRAILLE LINE:  'Enter a bug # or some search terms:  $l'",
     "     VISIBLE:  'terms:  $l', cursor=8",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'GNOME Bug Tracking System page tab.'",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'Enter a bug # or some search terms: entry.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Ctrl>w"))
sequence.append(utils.AssertPresentationAction(
    "4. Close third page tab - land in second page",
    ["KNOWN ISSUE: EOCs",
     "BRAILLE LINE:  'Firefox application Orca - GNOME Live! - Firefox Nightly frame Browser tabs tool bar Orca - GNOME Live! page tab'",
     "     VISIBLE:  'Orca - GNOME Live! page tab', cursor=1",
     "BRAILLE LINE:  '\ufffc\ufffc'",
     "     VISIBLE:  '\ufffc\ufffc', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Orca - GNOME Live! page tab.'",
     "SPEECH OUTPUT: 'leaving form.'",
     "SPEECH OUTPUT: 'document web'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
