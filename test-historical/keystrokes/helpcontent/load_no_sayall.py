#!/usr/bin/python

"""Test of learn mode."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F1"))
sequence.append(utils.AssertPresentationAction(
    "1. F1 for help",
    ["BRAILLE LINE:  'yelp application Orca Screen Reader frame'",
     "     VISIBLE:  'Orca Screen Reader frame', cursor=1",
     "BRAILLE LINE:  ' Orca's logo Orca Screen Reader h1'",
     "     VISIBLE:  'Orca's logo Orca Screen Reader h', cursor=1",
     "BRAILLE LINE:  'Finished loading Orca Screen Reader.'",
     "     VISIBLE:  'Finished loading Orca Screen Rea', cursor=0",
     "BRAILLE LINE:  ' Orca's logo Orca Screen Reader h1'",
     "     VISIBLE:  'Orca's logo Orca Screen Reader h', cursor=1",
     "SPEECH OUTPUT: 'F1 '",
     "SPEECH OUTPUT: 'Orca Screen Reader frame'",
     "SPEECH OUTPUT: 'Finished loading Orca Screen Reader.' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
