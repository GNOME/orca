#!/usr/bin/python

"""Test presentation of checked menu item state."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Arrow to the Freeze menu item (unchecked)",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame (1 dialog) fruit.ods - LibreOffice Calc root pane Freeze'",
     "     VISIBLE:  'Freeze', cursor=1",
     "SPEECH OUTPUT: 'Freeze'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Arrow to the Freeze menu item (checked)",
    ["BRAILLE LINE:  'soffice application fruit.ods - LibreOffice Calc frame (1 dialog) fruit.ods - LibreOffice Calc root pane <x> Freeze'",
     "     VISIBLE:  '<x> Freeze', cursor=1",
     "SPEECH OUTPUT: 'Freeze checked'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>w"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
