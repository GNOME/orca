#!/usr/bin/python

"""Test of ARIA menu presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Alt>m"))
sequence.append(utils.AssertPresentationAction(
    "1. Move to the menu",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Edit menu'",
     "     VISIBLE:  'Edit menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Edit menu'",
     "     VISIBLE:  'Edit menu', cursor=1",
     "SPEECH OUTPUT: 'Edit menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. basic whereAmI",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Edit menu'",
     "     VISIBLE:  'Edit menu', cursor=1",
     "SPEECH OUTPUT: 'ARIA Spreadsheet and Menubar - Mozilla Firefox frame'",
     "SPEECH OUTPUT: 'Edit menu 1 of 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Move to View",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded View menu'",
     "     VISIBLE:  'View menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded View menu'",
     "     VISIBLE:  'View menu', cursor=1",
     "SPEECH OUTPUT: 'View menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Move to Themes",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded menu'",
     "     VISIBLE:  'menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Themes          > menu'",
     "     VISIBLE:  'Themes          > menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Themes          > menu'",
     "     VISIBLE:  'Themes          > menu', cursor=1",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Themes          > menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Move to basic grey",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded menu'",
     "     VISIBLE:  'menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Basic Grey'",
     "     VISIBLE:  'Basic Grey', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Basic Grey'",
     "     VISIBLE:  'Basic Grey', cursor=1",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Basic Grey'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Move to the blues",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded The Blues'",
     "     VISIBLE:  'The Blues', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded The Blues'",
     "     VISIBLE:  'The Blues', cursor=1",
     "SPEECH OUTPUT: 'The Blues'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Move to garden",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Garden'",
     "     VISIBLE:  'Garden', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Garden'",
     "     VISIBLE:  'Garden', cursor=1",
     "SPEECH OUTPUT: 'Garden'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Move to in the pink",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded In the Pink grayed'",
     "     VISIBLE:  'In the Pink grayed', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded In the Pink grayed'",
     "     VISIBLE:  'In the Pink grayed', cursor=1",
     "SPEECH OUTPUT: 'In the Pink grayed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Move to rose",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Rose'",
     "     VISIBLE:  'Rose', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Rose'",
     "     VISIBLE:  'Rose', cursor=1",
     "SPEECH OUTPUT: 'Rose'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Move back to Themes",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Themes          > menu'",
     "     VISIBLE:  'Themes          > menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Themes          > menu'",
     "     VISIBLE:  'Themes          > menu', cursor=1",
     "SPEECH OUTPUT: 'Themes          > menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Move to hide",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Hide'",
     "     VISIBLE:  'Hide', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Hide'",
     "     VISIBLE:  'Hide', cursor=1",
     "SPEECH OUTPUT: 'Hide'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Move to show",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Show'",
     "     VISIBLE:  'Show', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded Show'",
     "     VISIBLE:  'Show', cursor=1",
     "SPEECH OUTPUT: 'Show'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Move to more",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded More                > menu'",
     "     VISIBLE:  'More                > menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded More                > menu'",
     "     VISIBLE:  'More                > menu', cursor=1",
     "SPEECH OUTPUT: 'More                > menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "14. Move to one",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded menu'",
     "     VISIBLE:  'menu', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded one'",
     "     VISIBLE:  'one', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded one'",
     "     VISIBLE:  'one', cursor=1",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Move to two",
    ["BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded two'",
     "     VISIBLE:  'two', cursor=1",
     "BRAILLE LINE:  'ARIA Spreadsheet and Menubar embedded two'",
     "     VISIBLE:  'two', cursor=1",
     "SPEECH OUTPUT: 'two'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
