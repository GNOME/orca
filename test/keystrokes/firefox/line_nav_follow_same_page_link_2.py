#!/usr/bin/python

"""Test of navigation by same-page links on the Orca wiki."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("H"))
sequence.append(KeyComboAction("H"))
for i in range(4):
    sequence.append(KeyComboAction("Tab"))
    sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to activate the same-page link for the About heading",
    ["BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down to read the text under the About heading",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
