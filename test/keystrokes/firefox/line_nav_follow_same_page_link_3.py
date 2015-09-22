#!/usr/bin/python

"""Test of line nav after loading a same-page link."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(WaitForDocLoad())
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down to what should be the text below the About heading",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
