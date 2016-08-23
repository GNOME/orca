#!/usr/bin/python

"""Test of check menu item output."""

from macaroon.playback import *

sequence = MacroSequence()
import utils

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Arrow to check menu item - checked",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame <x> Bold check menu item(Ctrl+B)'",
     "     VISIBLE:  '<x> Bold check menu item(Ctrl+B)', cursor=1",
     "SPEECH OUTPUT: 'Bold check menu item checked Ctrl+B.'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Arrow to check menu item - not checked",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame < > Bold check menu item(Ctrl+B)'",
     "     VISIBLE:  '< > Bold check menu item(Ctrl+B)', cursor=1",
     "SPEECH OUTPUT: 'Bold check menu item not checked Ctrl+B.'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Arrow to check menu item - checked",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame <x> Bold check menu item(Ctrl+B)'",
     "     VISIBLE:  '<x> Bold check menu item(Ctrl+B)', cursor=1",
     "SPEECH OUTPUT: 'Bold check menu item checked Ctrl+B.'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
