#!/usr/bin/python

"""Test to verify SayAll works in Writer."""

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(2000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. Say all",
    ["SPEECH OUTPUT: 'December 2006'",
     "SPEECH OUTPUT: 'This is a test.'",
     "SPEECH OUTPUT: 'Sun'",
     "SPEECH OUTPUT: 'Mon'",
     "SPEECH OUTPUT: 'Tue'",
     "SPEECH OUTPUT: 'Wed'",
     "SPEECH OUTPUT: 'Thu'",
     "SPEECH OUTPUT: 'Fri'",
     "SPEECH OUTPUT: 'Sat'",
     "SPEECH OUTPUT: '1'",
     "SPEECH OUTPUT: '2'",
     "SPEECH OUTPUT: '3'",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: '6'",
     "SPEECH OUTPUT: '7'",
     "SPEECH OUTPUT: '8'",
     "SPEECH OUTPUT: '9'",
     "SPEECH OUTPUT: '10'",
     "SPEECH OUTPUT: '11'",
     "SPEECH OUTPUT: '12'",
     "SPEECH OUTPUT: '13'",
     "SPEECH OUTPUT: '14'",
     "SPEECH OUTPUT: '15'",
     "SPEECH OUTPUT: '16'",
     "SPEECH OUTPUT: '17'",
     "SPEECH OUTPUT: '18'",
     "SPEECH OUTPUT: '19'",
     "SPEECH OUTPUT: '20'",
     "SPEECH OUTPUT: '21'",
     "SPEECH OUTPUT: '22'",
     "SPEECH OUTPUT: '23'",
     "SPEECH OUTPUT: '24'",
     "SPEECH OUTPUT: '25'",
     "SPEECH OUTPUT: '26'",
     "SPEECH OUTPUT: '27'",
     "SPEECH OUTPUT: '28'",
     "SPEECH OUTPUT: '29'",
     "SPEECH OUTPUT: '30'",
     "SPEECH OUTPUT: '31'",
     "SPEECH OUTPUT: 'So is this.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
