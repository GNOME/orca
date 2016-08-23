#!/usr/bin/python

"""Test of icon output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Images"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. bin icon",
    ["BRAILLE LINE:  'gtk3-demo application Icon View Basics frame bin icon'",
     "     VISIBLE:  'bin icon', cursor=1",
     "SPEECH OUTPUT: 'bin icon.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "2. Review current line",
    ["KNOWN ISSUE: This and all the subsequent assertions are broken due to flat review bugs",
     "BRAILLE LINE:  '   vertical scroll bar 0% $l'",
     "     VISIBLE:  '   vertical scroll bar 0% $l', cursor=1",
     "SPEECH OUTPUT: 'vertical scroll bar 0 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "3. Review current word",
    ["BRAILLE LINE:  '   vertical scroll bar 0% $l'",
     "     VISIBLE:  '   vertical scroll bar 0% $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next word",
    ["BRAILLE LINE:  '   vertical scroll bar 0% $l'",
     "     VISIBLE:  '   vertical scroll bar 0% $l', cursor=2",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current char",
    ["BRAILLE LINE:  '   vertical scroll bar 0% $l'",
     "     VISIBLE:  '   vertical scroll bar 0% $l', cursor=2",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Review item below",
    ["BRAILLE LINE:  '   $l'",
     "     VISIBLE:  '   $l', cursor=2",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Review item below",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=2",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Review item above",
    ["BRAILLE LINE:  '   $l'",
     "     VISIBLE:  '   $l', cursor=2",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Review item above",
    ["BRAILLE LINE:  '   vertical scroll bar 0% $l'",
     "     VISIBLE:  '   vertical scroll bar 0% $l', cursor=2",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next line",
    ["BRAILLE LINE:  '   $l'",
     "     VISIBLE:  '   $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next word",
    ["BRAILLE LINE:  '   $l'",
     "     VISIBLE:  '   $l', cursor=2",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next char",
    ["BRAILLE LINE:  '   $l'",
     "     VISIBLE:  '   $l', cursor=3",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "13. Review previous line",
    ["BRAILLE LINE:  '   vertical scroll bar 0% $l'",
     "     VISIBLE:  '   vertical scroll bar 0% $l', cursor=1",
     "SPEECH OUTPUT: 'vertical scroll bar 0 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "14. Review previous line",
    ["BRAILLE LINE:  'Up Home $l'",
     "     VISIBLE:  'Up Home $l', cursor=1",
     "SPEECH OUTPUT: 'Up Home'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "15. Review previous line",
    [""]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
