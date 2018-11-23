#!/usr/bin/python

"""Test presentation of checked menu item state."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Arrow to the check menu item (checked)",
    ["BRAILLE LINE:  'soffice application <x> Formula Bar check menu item'",
     "     VISIBLE:  '<x> Formula Bar check menu item', cursor=1",
     "SPEECH OUTPUT: 'Formula Bar check menu item checked.'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Arrow to the check menu item (unchecked)",
    ["BRAILLE LINE:  'soffice application View menu < > Formula Bar check menu item'",
     "     VISIBLE:  '< > Formula Bar check menu item', cursor=1",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Formula Bar check menu item not checked.'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
