#!/usr/bin/python

"""Test of HTML combo box presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to Severity combo box",
    ["BRAILLE LINE:  'Severity: Severity Severity combo box'",
     "     VISIBLE:  'Severity Severity combo box', cursor=10",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  ':  $l'",
     "     VISIBLE:  ':  $l', cursor=3",
     "SPEECH OUTPUT: 'Severity normal combo box'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["KNOWN ISSUE: We want to present the displayed item",
     "BRAILLE LINE:  'Severity Severity combo box'",
     "     VISIBLE:  'Severity Severity combo box', cursor=10",
     "SPEECH OUTPUT: 'Severity'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'normal'",
     "SPEECH OUTPUT: '4 of 7'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to Priority link",
    ["BRAILLE LINE:  'Priority'",
     "     VISIBLE:  'Priority', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "BRAILLE LINE:  'Priority:  combo box'",
     "     VISIBLE:  'Priority:  combo box', cursor=1",
     "SPEECH OUTPUT: 'Priority'",
     "SPEECH OUTPUT: 'link' voice=hyperlink",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to Priority combo box",
    ["BRAILLE LINE:  'Priority:  combo box'",
     "     VISIBLE:  'Priority:  combo box', cursor=11",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  ':  $l'",
     "     VISIBLE:  ':  $l', cursor=3",
     "SPEECH OUTPUT: 'Priority: Normal combo box'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to Resolution combo box",
    ["KNOWN ISSUE: We shouldn't be displaying the EOC",
     "BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "BRAILLE LINE:  '\ufffc $l'",
     "     VISIBLE:  '\ufffc $l', cursor=1",
     "SPEECH OUTPUT: 'Resolution: FIXED combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Change selection Down: WONTFIX",
    ["BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "SPEECH OUTPUT: 'WONTFIX'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Change selection Up: FIXED",
    ["BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "SPEECH OUTPUT: 'FIXED'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Alt Down to Expand",
    ["KNOWN ISSUE: We are presenting nothing here",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Change selection Down: WONTFIX",
    ["BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "SPEECH OUTPUT: 'WONTFIX'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "10. Return to collapse combo box",
    ["BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "SPEECH OUTPUT: 'Resolution: WONTFIX combo box'",
     "SPEECH OUTPUT: 'WONTFIX'",
     "SPEECH OUTPUT: 'combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "11. Tab to Version combo box",
    ["BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=1",
     "SPEECH OUTPUT: 'Version 2.16 combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("a"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Toggle Browse Mode",
    ["BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))


sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Left out of combo box",
    ["BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=1",
     "BRAILLE LINE:  'Version combo box'",
     "     VISIBLE:  'Version combo box', cursor=8",
     "SPEECH OUTPUT: 'Version 2.16'",
     "SPEECH OUTPUT: 'combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Component'",
     "     VISIBLE:  'Component', cursor=1",
     "SPEECH OUTPUT: 'Component'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
