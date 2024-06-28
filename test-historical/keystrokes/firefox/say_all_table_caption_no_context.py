#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Below is a table, with some sample table data'",
     "SPEECH OUTPUT: 'this is a caption for this table'",
     "SPEECH OUTPUT: 'caption'",
     "SPEECH OUTPUT: 'col1'",
     "SPEECH OUTPUT: 'column header'",
     "SPEECH OUTPUT: 'col2'",
     "SPEECH OUTPUT: 'column header'",
     "SPEECH OUTPUT: 'col3'",
     "SPEECH OUTPUT: 'column header'",
     "SPEECH OUTPUT: '1'",
     "SPEECH OUTPUT: '2'",
     "SPEECH OUTPUT: '3'",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: '6'",
     "SPEECH OUTPUT: '7'",
     "SPEECH OUTPUT: '8'",
     "SPEECH OUTPUT: '9'",
     "SPEECH OUTPUT: 'hope the table looks pretty'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
