#!/usr/bin/python

"""Test of Orca's presentation of a combo box."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("<Control><Shift>Left"))

sequence.append(KeyComboAction("<Alt>o"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("<Control>Page_Down"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Move to Strikethrough",
    ["BRAILLE LINE:  'soffice application Character dialog Font Effects page tab Strikethrough: (Without) combo box'",
     "     VISIBLE:  'Strikethrough: (Without) combo b', cursor=16",
     "SPEECH OUTPUT: 'Strikethrough: (Without) combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["KNOWN ISSUE: We seem to be presenting extra context here",
     "BRAILLE LINE:  'soffice application Character dialog Font Effects page tab Strikethrough: Single combo box Single list item'",
     "     VISIBLE:  'Single list item', cursor=1",
     "SPEECH OUTPUT: 'Character dialog'",
     "SPEECH OUTPUT: 'Font Effects page tab.'",
     "SPEECH OUTPUT: 'Single.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow",
    ["BRAILLE LINE:  'soffice application Character dialog Font Effects page tab Strikethrough: (Without) combo box (Without) list item'",
     "     VISIBLE:  '(Without) list item', cursor=1",
     "SPEECH OUTPUT: '(Without)'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
