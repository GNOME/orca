#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["KNOWN ISSUE: We are guessing the list box label here; we should not",
     "SPEECH OUTPUT: 'Type something here: entry'",
     "SPEECH OUTPUT: 'Magic disappearing text trick: entry tab to me and I disappear'",
     "SPEECH OUTPUT: 'Tell me a secret: password text'",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:",
     " entry'",
     "SPEECH OUTPUT: 'Check one or more: Red check box not checked Blue check box not checked Green check box not checked'",
     "SPEECH OUTPUT: 'Make a selection: Water combo box'",
     "SPEECH OUTPUT: 'Which sports do you like?",
     " Which sports do you like? Hockey multi-select List with 4 items'",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker image'",
     "SPEECH OUTPUT: '",
     "Ain't he handsome (please say yes)? not selected radio button Yes not selected radio button No'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
