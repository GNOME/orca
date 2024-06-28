#!/usr/bin/python

"""Test of menu and menu item output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>r"))
sequence.append(PauseAction(3000))

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
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "2. Review current line",
    ["BRAILLE LINE:  'Color <x> Red $l'",
     "     VISIBLE:  'Color <x> Red $l', cursor=1",
     "SPEECH OUTPUT: 'Color checked Red'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "3. Review next line",
    ["BRAILLE LINE:  'Shape < > Green $l'",
     "     VISIBLE:  'Shape < > Green $l', cursor=1",
     "SPEECH OUTPUT: 'Shape not checked Green'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=1",
     "SPEECH OUTPUT: 'checked Bold not checked Blue'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current word",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next word",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=5",
     "SPEECH OUTPUT: 'Bold'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "8. Review current word",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=5",
     "SPEECH OUTPUT: 'Bold'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "9. Review current char",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=5",
     "SPEECH OUTPUT: 'B'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next word",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=10",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next char",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=14",
     "SPEECH OUTPUT: 'B'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next char",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=15",
     "SPEECH OUTPUT: 'l'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "13. Review next char",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=16",
     "SPEECH OUTPUT: 'u'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "14. Review previous char",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=15",
     "SPEECH OUTPUT: 'l'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "15. Review previous char",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=14",
     "SPEECH OUTPUT: 'B'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "16. Review previous word",
    ["BRAILLE LINE:  '<x> Bold < > Blue $l'",
     "     VISIBLE:  '<x> Bold < > Blue $l', cursor=10",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "17. Review previous line",
    ["BRAILLE LINE:  'Shape < > Green $l'",
     "     VISIBLE:  'Shape < > Green $l', cursor=1",
     "SPEECH OUTPUT: 'Shape not checked Green'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
