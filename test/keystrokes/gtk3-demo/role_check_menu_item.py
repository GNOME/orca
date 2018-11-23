#!/usr/bin/python

"""Test of check menu item output."""

from macaroon.playback import *

sequence = MacroSequence()
import utils

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Arrow to first check menu item - not checked",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame < > Hide Titlebar when maximized check menu item'",
     "     VISIBLE:  '< > Hide Titlebar when maximized', cursor=1",
     "SPEECH OUTPUT: 'Hide Titlebar when maximized check menu item not checked.'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Arrow to first check menu item - checked",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame <x> Hide Titlebar when maximized check menu item'",
     "     VISIBLE:  '<x> Hide Titlebar when maximized', cursor=1",
     "SPEECH OUTPUT: 'Hide Titlebar when maximized check menu item checked.'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Arrow to first check menu item - not checked",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame < > Hide Titlebar when maximized check menu item'",
     "     VISIBLE:  '< > Hide Titlebar when maximized', cursor=1",
     "SPEECH OUTPUT: 'Hide Titlebar when maximized check menu item not checked.'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
