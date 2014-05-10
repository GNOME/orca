#!/usr/bin/python

"""Test of Orca's presentation of a combo box."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("<Control><Shift>Left"))

sequence.append(KeyComboAction("<Alt>o"))
sequence.append(TypeAction("h"))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Move to Strikethrough",
    ["KNOWN ISSUE: Too chatty",
     "BRAILLE LINE:  'soffice application Character frame Character dialog Font Effects page tab Options panel (Without) combo box'",
     "     VISIBLE:  '(Without) combo box', cursor=1",
     "BRAILLE LINE:  'soffice application Character frame Character dialog Font Effects page tab Options panel (Without) $l'",
     "     VISIBLE:  '(Without) $l', cursor=1",
     "BRAILLE LINE:  'soffice application Character frame Character dialog Font Effects page tab Options panel  combo box(Without) (Without) list item'",
     "     VISIBLE:  '(Without) list item', cursor=1",
     "SPEECH OUTPUT: '(Without) combo box'",
     "SPEECH OUTPUT: 'text (Without)'",
     "SPEECH OUTPUT: '(Without)'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
