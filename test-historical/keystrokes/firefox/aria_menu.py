#!/usr/bin/python

"""Test of ARIA menu presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Alt>m"))
sequence.append(utils.AssertPresentationAction(
    "1. Move to the menu",
    ["BRAILLE LINE:  'Edit menu'",
     "     VISIBLE:  'Edit menu', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'Edit menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. basic whereAmI",
    ["BRAILLE LINE:  'Edit menu'",
     "     VISIBLE:  'Edit menu', cursor=1",
     "SPEECH OUTPUT: 'Edit menu.'",
     "SPEECH OUTPUT: '1 of 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Move to View",
    ["BRAILLE LINE:  'View menu'",
     "     VISIBLE:  'View menu', cursor=1",
     "SPEECH OUTPUT: 'View menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Move to Themes",
    ["BRAILLE LINE:  'Themes          > menu'",
     "     VISIBLE:  'Themes          > menu', cursor=1",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Themes          > menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Move to basic grey",
    ["BRAILLE LINE:  'Basic Grey'",
     "     VISIBLE:  'Basic Grey', cursor=1",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Basic Grey.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Move to the blues",
    ["BRAILLE LINE:  'The Blues'",
     "     VISIBLE:  'The Blues', cursor=1",
     "SPEECH OUTPUT: 'The Blues.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Move to garden",
    ["BRAILLE LINE:  'Garden'",
     "     VISIBLE:  'Garden', cursor=1",
     "SPEECH OUTPUT: 'Garden.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Move to in the pink",
    ["BRAILLE LINE:  'In the Pink grayed'",
     "     VISIBLE:  'In the Pink grayed', cursor=1",
     "SPEECH OUTPUT: 'In the Pink grayed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Move to rose",
    ["BRAILLE LINE:  'Rose'",
     "     VISIBLE:  'Rose', cursor=1",
     "SPEECH OUTPUT: 'Rose.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Move back to Themes",
    ["BRAILLE LINE:  'Themes          > menu'",
     "     VISIBLE:  'Themes          > menu', cursor=1",
     "SPEECH OUTPUT: 'Themes          > menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Move to hide",
    ["BRAILLE LINE:  'Hide'",
     "     VISIBLE:  'Hide', cursor=1",
     "SPEECH OUTPUT: 'Hide.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Move to show",
    ["BRAILLE LINE:  'Show'",
     "     VISIBLE:  'Show', cursor=1",
     "SPEECH OUTPUT: 'Show.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Move to more",
    ["BRAILLE LINE:  'More                > menu'",
     "     VISIBLE:  'More                > menu', cursor=1",
     "SPEECH OUTPUT: 'More                > menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "14. Move to one",
    ["BRAILLE LINE:  'one'",
     "     VISIBLE:  'one', cursor=1",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'one.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Move to two",
    ["BRAILLE LINE:  'two'",
     "     VISIBLE:  'two', cursor=1",
     "SPEECH OUTPUT: 'two.'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
