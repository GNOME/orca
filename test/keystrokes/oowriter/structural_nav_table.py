#!/usr/bin/python

"""Test for structural navigation amongst table cells in Writer."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("z"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Toggle structural navigation on",
    ["SPEECH OUTPUT: 'Structural navigation keys on.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "1. Alt Shift Left.",
    ["SPEECH OUTPUT: '3'",
     "SPEECH OUTPUT: 'Row 3, column 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Alt Shift Left.",
    ["SPEECH OUTPUT: 'Beginning of row.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "3. Alt Shift Right.",
    ["SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: 'Row 3, column 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "4. Alt Shift Right.",
    ["SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: 'Row 3, column 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "5. Alt Shift Right.",
    ["SPEECH OUTPUT: '6'",
     "SPEECH OUTPUT: '7'",
     "SPEECH OUTPUT: 'Row 3, column 4.'",
     "SPEECH OUTPUT: 'Cell spans 2 columns'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "6. Alt Shift Up.",
    ["KNOWN ISSUE: We should say 'blank' here.",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Row 2, column 4.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "7. Alt Shift Up.",
    ["SPEECH OUTPUT: 'Wed'",
     "SPEECH OUTPUT: 'Row 1, column 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Alt Shift Up.",
    ["SPEECH OUTPUT: 'Top of column.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>End"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "9. Alt Shift End.",
    ["KNOWN ISSUE: We should say 'blank' here.",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Row 7, column 7.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Alt Shift Down.",
    ["SPEECH OUTPUT: 'Bottom of column.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Alt Shift Right.",
    ["SPEECH OUTPUT: 'End of row.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "12. Alt Shift Home.",
    ["SPEECH OUTPUT: 'Sun'",
     "SPEECH OUTPUT: 'Row 1, column 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Alt Shift Up.",
    ["SPEECH OUTPUT: 'Top of column.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Up Arrow out of table.",
    ["SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Alt Shift Up when not in a table.",
    ["SPEECH OUTPUT: 'Not in a table.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("z"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "16. Toggle structural navigation off",
    ["SPEECH OUTPUT: 'Structural navigation keys off.' voice=system"]))

sequence.append(KeyComboAction("<Control>W"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
