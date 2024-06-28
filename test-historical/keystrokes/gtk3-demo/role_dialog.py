#!/usr/bin/python

"""Test of dialog presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Expander"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Dialog automatic reading",
    ["BRAILLE LINE:  'gtk3-demo application window Expander $l'",
     "     VISIBLE:  'Expander $l', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Error alert'",
     "     VISIBLE:  'Error alert', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Error alert & y Details: collapsed toggle button'",
     "     VISIBLE:  '& y Details: collapsed toggle bu', cursor=1",
     "SPEECH OUTPUT: 'Error alert.'",
     "SPEECH OUTPUT: 'Something went wrong Here are some more details but not the full story.'",
     "SPEECH OUTPUT: 'Details: toggle button collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Dialog Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Error alert & y Details: collapsed toggle button'",
     "     VISIBLE:  '& y Details: collapsed toggle bu', cursor=1",
     "SPEECH OUTPUT: 'Details: toggle button collapsed'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
