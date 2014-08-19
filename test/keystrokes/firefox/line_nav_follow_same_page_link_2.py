#!/usr/bin/python

"""Test of navigation by same-page links on the Orca wiki."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
for i in range(25):
    sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to activate the same-page link for the About heading",
    ["KNOWN ISSUE: We are not speaking this.",
     "BRAILLE LINE:  '2.About'",
     "     VISIBLE:  '2.About', cursor=3"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down to read the text under the About heading",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
