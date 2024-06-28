#!/usr/bin/python

from macaroon.playback import *
import utils

utils.setClipboardText("Hello world")

sequence = MacroSequence()
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>v"))
sequence.append(utils.AssertPresentationAction(
    "1. Paste",
    ["BRAILLE LINE:  '$ Hello world'",
     "     VISIBLE:  '$ Hello world', cursor=14",
     "BRAILLE LINE:  'Pasted contents from clipboard.'",
     "     VISIBLE:  'Pasted contents from clipboard.', cursor=0",
     "BRAILLE LINE:  '$ Hello world'",
     "     VISIBLE:  '$ Hello world', cursor=14",
     "SPEECH OUTPUT: 'Pasted contents from clipboard.' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
