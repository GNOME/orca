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
    ["BRAILLE LINE:  'gtk3-demo application Icon View Basics frame layered pane bin icon'",
     "     VISIBLE:  'bin icon', cursor=1",
     "SPEECH OUTPUT: 'bin icon.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "2. Review current line",
    ["BRAILLE LINE:  'bin boot dev $l'",
     "     VISIBLE:  'bin boot dev $l', cursor=1",
     "SPEECH OUTPUT: 'bin boot dev'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "3. Review current word",
    ["BRAILLE LINE:  'bin boot dev $l'",
     "     VISIBLE:  'bin boot dev $l', cursor=1",
     "SPEECH OUTPUT: 'bin'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next word",
    ["BRAILLE LINE:  'bin boot dev $l'",
     "     VISIBLE:  'bin boot dev $l', cursor=5",
     "SPEECH OUTPUT: 'boot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current char",
    ["BRAILLE LINE:  'bin boot dev $l'",
     "     VISIBLE:  'bin boot dev $l', cursor=5",
     "SPEECH OUTPUT: 'boot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Review item below",
    ["BRAILLE LINE:  'etc home lib $l'",
     "     VISIBLE:  'etc home lib $l', cursor=5",
     "SPEECH OUTPUT: 'home'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Review item below",
    ["BRAILLE LINE:  'lib64 lost+found media $l'",
     "     VISIBLE:  'lib64 lost+found media $l', cursor=7",
     "SPEECH OUTPUT: 'lost+found'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Review item above",
    ["BRAILLE LINE:  'etc home lib $l'",
     "     VISIBLE:  'etc home lib $l', cursor=5",
     "SPEECH OUTPUT: 'home'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Review item above",
    ["BRAILLE LINE:  'bin boot dev $l'",
     "     VISIBLE:  'bin boot dev $l', cursor=5",
     "SPEECH OUTPUT: 'boot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next line",
    ["BRAILLE LINE:  'etc home lib $l'",
     "     VISIBLE:  'etc home lib $l', cursor=1",
     "SPEECH OUTPUT: 'etc home lib'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next word",
    ["BRAILLE LINE:  'etc home lib $l'",
     "     VISIBLE:  'etc home lib $l', cursor=5",
     "SPEECH OUTPUT: 'home'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next char",
    ["BRAILLE LINE:  'etc home lib $l'",
     "     VISIBLE:  'etc home lib $l', cursor=10",
     "SPEECH OUTPUT: 'lib'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "13. Review previous line",
    ["BRAILLE LINE:  'bin boot dev $l'",
     "     VISIBLE:  'bin boot dev $l', cursor=1",
     "SPEECH OUTPUT: 'bin boot dev'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "14. Review previous line",
    ["BRAILLE LINE:  'vertical scroll bar 0% $l'",
     "     VISIBLE:  'vertical scroll bar 0% $l', cursor=1",
     "SPEECH OUTPUT: 'vertical scroll bar 0 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "15. Review previous line",
    ["BRAILLE LINE:  'Up Home $l'",
     "     VISIBLE:  'Up Home $l', cursor=1",
     "SPEECH OUTPUT: 'Up Home'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "16. Review previous line",
    [""]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
