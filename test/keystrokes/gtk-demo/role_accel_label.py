#!/usr/bin/python

"""Test of menu accelerator label output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(utils.AssertPresentationAction(
    "1. Initial menu and menu item",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Preferences menu'",
     "     VISIBLE:  'Preferences menu', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Application Window frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu.'",
     "SPEECH OUTPUT: 'Color menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu'",
     "SPEECH OUTPUT: 'Color menu.'",
     "SPEECH OUTPUT: '1 of 4.'",
     "SPEECH OUTPUT: 'C'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
