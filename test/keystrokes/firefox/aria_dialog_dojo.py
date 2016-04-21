#!/usr/bin/python

"""Test of Dojo dialog presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Launch dialog",
    ["BRAILLE LINE:  'TabContainer Dialog dialog'",
     "     VISIBLE:  'TabContainer Dialog dialog', cursor=1",
     "BRAILLE LINE:  'First tab page tab'",
     "     VISIBLE:  'First tab page tab', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'TabContainer Dialog This is the first tab.  Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut ligula. Proin porta rutrum lacus. Etiam consequat scelerisque quam. Nulla facilisi. Maecenas luctus venenatis nulla. In sit amet dui non mi semper iaculis. Sed molestie tortor at ipsum. Morbi dictum rutrum magna. Sed vitae risus.'",
     "SPEECH OUTPUT: 'First tab page tab.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereAmI",
    ["BRAILLE LINE:  'First tab page tab'",
     "     VISIBLE:  'First tab page tab', cursor=1",
     "BRAILLE LINE:  'First tab page tab'",
     "     VISIBLE:  'First tab page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list.",
     "SPEECH OUTPUT: 'First tab page tab.",
     "SPEECH OUTPUT: '1 of 2'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
