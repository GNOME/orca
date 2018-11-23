#!/usr/bin/python

"""Test of menu and menu item output."""

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
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Get into Color menu",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Preferences menu <x> Red check menu item(Ctrl+R)'",
     "     VISIBLE:  '<x> Red check menu item(Ctrl+R)', cursor=1",
     "SPEECH OUTPUT: 'Red check menu item checked Ctrl+R.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Preferences menu <x> Red check menu item(Ctrl+R)'",
     "     VISIBLE:  '<x> Red check menu item(Ctrl+R)', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu'",
     "SPEECH OUTPUT: 'Color menu'",
     "SPEECH OUTPUT: 'Red check menu item checked.'",
     "SPEECH OUTPUT: 'Ctrl+R.'",
     "SPEECH OUTPUT: '1 of 4.'",
     "SPEECH OUTPUT: 'R'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Get out of Color menu",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Color menu.'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
