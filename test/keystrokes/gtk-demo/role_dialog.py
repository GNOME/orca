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
    ["BRAILLE LINE:  'gtk-demo application window Expander $l'",
     "     VISIBLE:  'Expander $l', cursor=1",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog'",
     "     VISIBLE:  'GtkExpander dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog & y Details collapsed toggle button'",
     "     VISIBLE:  '& y Details collapsed toggle but', cursor=1",
     "SPEECH OUTPUT: 'GtkExpander Expander demo. Click on the triangle for details.'",
     "SPEECH OUTPUT: 'Details toggle button collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Dialog Where Am I",
    ["BRAILLE LINE:  'gtk-demo application GtkExpander dialog & y Details collapsed toggle button'",
     "     VISIBLE:  '& y Details collapsed toggle but', cursor=1",
     "SPEECH OUTPUT: 'Details toggle button collapsed'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
