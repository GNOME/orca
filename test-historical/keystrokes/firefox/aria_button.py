#!/usr/bin/python

"""Test of ARIA button presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to Tracking number text entry",
    ["BRAILLE LINE:  'Tracking number  $l'",
     "     VISIBLE:  'Tracking number  $l', cursor=17",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Tracking number entry.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to Check Now push button",
    ["BRAILLE LINE:  'Tracking number  $l'",
     "     VISIBLE:  'Tracking number  $l', cursor=17",
     "BRAILLE LINE:  'Check Now push button'",
     "     VISIBLE:  'Check Now push button', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Check Now push button Check to see if your order has been shipped.'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic whereamI",
    ["BRAILLE LINE:  'Check Now push button'",
     "     VISIBLE:  'Check Now push button', cursor=1",
     "BRAILLE LINE:  'Check Now push button'",
     "     VISIBLE:  'Check Now push button', cursor=1",
     "SPEECH OUTPUT: 'Check Now push button Check to see if your order has been shipped.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
