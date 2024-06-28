#!/usr/bin/python

"""Test of menu and menu item output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(utils.AssertPresentationAction(
    "1. Initial menu and menu item",
    ["BRAILLE LINE:  'soffice application View menu'",
     "     VISIBLE:  'soffice application View menu', cursor=21",
     "BRAILLE LINE:  'soffice application View menu &=y Normal radio menu item'",
     "     VISIBLE:  '&=y Normal radio menu item', cursor=1",
     "SPEECH OUTPUT: 'View menu.'",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Normal selected radio menu item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  'soffice application View menu & y Web radio menu item'",
     "     VISIBLE:  '& y Web radio menu item', cursor=1",
     "SPEECH OUTPUT: 'Web not selected radio menu item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "3. Review currernt line",
    ["BRAILLE LINE:  '& y Web $l'",
     "     VISIBLE:  '& y Web $l', cursor=1",
     "SPEECH OUTPUT: 'not selected Web'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  'separator $l'",
     "     VISIBLE:  'separator $l', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(KeyComboAction("KP_9"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "5. Review next line",
    ["BRAILLE LINE:  'Toolbars $l'",
     "     VISIBLE:  'Toolbars $l', cursor=1",
     "SPEECH OUTPUT: 'Toolbars'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  '<x> Status Bar $l'",
     "     VISIBLE:  '<x> Status Bar $l', cursor=1",
     "SPEECH OUTPUT: 'checked Status Bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line",
    ["BRAILLE LINE:  'Rulers $l'",
     "     VISIBLE:  'Rulers $l', cursor=1",
     "SPEECH OUTPUT: 'Rulers'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "8. Review current word",
    ["BRAILLE LINE:  'Rulers $l'",
     "     VISIBLE:  'Rulers $l', cursor=1",
     "SPEECH OUTPUT: 'Rulers'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next word",
    ["BRAILLE LINE:  'Scrollbars $l'",
     "     VISIBLE:  'Scrollbars $l', cursor=1",
     "SPEECH OUTPUT: 'Scrollbars'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "10. Review current char",
    ["BRAILLE LINE:  'Scrollbars $l'",
     "     VISIBLE:  'Scrollbars $l', cursor=1",
     "SPEECH OUTPUT: 'S'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next char",
    ["BRAILLE LINE:  'Scrollbars $l'",
     "     VISIBLE:  'Scrollbars $l', cursor=2",
     "SPEECH OUTPUT: 'c'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next word",
    ["BRAILLE LINE:  'separator $l'",
     "     VISIBLE:  'separator $l', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "13. Review current char",
    ["BRAILLE LINE:  'separator $l'",
     "     VISIBLE:  'separator $l', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "14. Review next char",
    ["BRAILLE LINE:  '<x> Text Boundaries $l'",
     "     VISIBLE:  '<x> Text Boundaries $l', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "15. Review previous char",
    ["BRAILLE LINE:  'separator $l'",
     "     VISIBLE:  'separator $l', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "16. Review previous char",
    ["BRAILLE LINE:  'Scrollbars $l'",
     "     VISIBLE:  'Scrollbars $l', cursor=10",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "17. Review previous word",
    ["BRAILLE LINE:  'Rulers $l'",
     "     VISIBLE:  'Rulers $l', cursor=1",
     "SPEECH OUTPUT: 'Rulers'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "18. Review previous line",
    ["BRAILLE LINE:  '<x> Status Bar $l'",
     "     VISIBLE:  '<x> Status Bar $l', cursor=1",
     "SPEECH OUTPUT: 'checked Status Bar'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
