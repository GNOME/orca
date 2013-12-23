#!/usr/bin/python

"""Test of dialog presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Expander"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Dialog automatic reading",
    ["KNOWN ISSUE: Depending on timing we present more than just the stuff below",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog'",
     "     VISIBLE:  'GtkExpander dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog & y Details collapsed toggle button'",
     "     VISIBLE:  '& y Details collapsed toggle but', cursor=1",
     "SPEECH OUTPUT: 'GtkExpander Expander demo. Click on the triangle for details.'",
     "SPEECH OUTPUT: 'Details toggle button collapsed'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Dialog Where Am I",
    ["BRAILLE LINE:  'gtk-demo application GtkExpander dialog & y Details collapsed toggle button'",
     "     VISIBLE:  '& y Details collapsed toggle but', cursor=1",
     "SPEECH OUTPUT: 'Details'",
     "SPEECH OUTPUT: 'toggle button collapsed'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
