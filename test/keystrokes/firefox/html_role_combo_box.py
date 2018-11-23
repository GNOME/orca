#!/usr/bin/python

"""Test of HTML combo box presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to Severity combo box",
    ["BRAILLE LINE:  'Severity normal combo box'",
     "     VISIBLE:  'Severity normal combo box', cursor=10",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Severity normal combo box.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["KNOWN ISSUE: The count is wrong.",
     "BRAILLE LINE:  'Severity normal combo box'",
     "     VISIBLE:  'Severity normal combo box', cursor=10",
     "BRAILLE LINE:  'Severity normal combo box'",
     "     VISIBLE:  'Severity normal combo box', cursor=10",
     "SPEECH OUTPUT: 'Severity combo box.'",
     "SPEECH OUTPUT: 'normal 2 of 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to Priority link",
    ["BRAILLE LINE:  'Priority'",
     "     VISIBLE:  'Priority', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Priority link.'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to Priority combo box",
    ["BRAILLE LINE:  'Priority'",
     "     VISIBLE:  'Priority', cursor=1",
     "BRAILLE LINE:  'Priority: Normal combo box'",
     "     VISIBLE:  'Priority: Normal combo box', cursor=11",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Priority: Normal combo box.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to Resolution combo box",
    ["BRAILLE LINE:  'Priority: Normal combo box'",
     "     VISIBLE:  'Priority: Normal combo box', cursor=11",
     "BRAILLE LINE:  'Resolution: FIXED combo box'",
     "     VISIBLE:  'Resolution: FIXED combo box', cursor=13",
     "SPEECH OUTPUT: 'Resolution: FIXED combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Change selection Down: WONTFIX",
    ["BRAILLE LINE:  'Resolution: WONTFIX combo box'",
     "     VISIBLE:  'Resolution: WONTFIX combo box', cursor=13",
     "SPEECH OUTPUT: 'WONTFIX.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Change selection Up: FIXED",
    ["BRAILLE LINE:  'Resolution: FIXED combo box'",
     "     VISIBLE:  'Resolution: FIXED combo box', cursor=13",
     "SPEECH OUTPUT: 'FIXED.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Alt Down to Expand",
    ["BRAILLE LINE:  'Firefox application Combo Box Regression Test - Firefox Nightly frame FIXED combo box FIXED'",
     "     VISIBLE:  'FIXED', cursor=1",
     "BRAILLE LINE:  'Firefox application Combo Box Regression Test - Firefox Nightly frame FIXED combo box'",
     "     VISIBLE:  'FIXED combo box', cursor=1",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'FIXED.'",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Change selection Down: WONTFIX",
    ["BRAILLE LINE:  'Firefox application Combo Box Regression Test - Firefox Nightly frame FIXED combo box WONTFIX'",
     "     VISIBLE:  'WONTFIX', cursor=1",
     "SPEECH OUTPUT: 'WONTFIX.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "10. Return to collapse combo box",
    ["BRAILLE LINE:  'Resolution: WONTFIX combo box'",
     "     VISIBLE:  'Resolution: WONTFIX combo box', cursor=13",
     "BRAILLE LINE:  'Resolution: WONTFIX combo box'",
     "     VISIBLE:  'Resolution: WONTFIX combo box', cursor=13",
     "SPEECH OUTPUT: 'Resolution: WONTFIX combo box.'",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "11. Tab to Version combo box",
    ["BRAILLE LINE:  'Version 2.16 combo box'",
     "     VISIBLE:  'Version 2.16 combo box', cursor=9",
     "SPEECH OUTPUT: 'Version 2.16 combo box.'"]))

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
    ["BRAILLE LINE:  'Version 2.16 combo box'",
     "     VISIBLE:  'Version 2.16 combo box', cursor=9",
     "BRAILLE LINE:  'Version 2.16 combo box'",
     "     VISIBLE:  'Version 2.16 combo box', cursor=7",
     "SPEECH OUTPUT: 'n'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Component'",
     "     VISIBLE:  'Component', cursor=1",
     "SPEECH OUTPUT: 'Component.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
