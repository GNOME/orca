#!/usr/bin/python

"""Test of menu and menu item output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(utils.AssertPresentationAction(
    "1. Initial menu and menu item",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar Toolbars menu'",
     "     VISIBLE:  'Toolbars menu', cursor=1",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Toolbars menu.'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar Sidebar menu'",
     "     VISIBLE:  'Sidebar menu', cursor=1",
     "SPEECH OUTPUT: 'Sidebar menu.'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "3. Review currernt line",
    ["BRAILLE LINE:  'Sidebar $l'",
     "     VISIBLE:  'Sidebar $l', cursor=1",
     "SPEECH OUTPUT: 'Sidebar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  'separator $l'",
     "     VISIBLE:  'separator $l', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "5. Review next line",
    ["BRAILLE LINE:  'Zoom $l'",
     "     VISIBLE:  'Zoom $l', cursor=1",
     "SPEECH OUTPUT: 'Zoom'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  'Page Style $l'",
     "     VISIBLE:  'Page Style $l', cursor=1",
     "SPEECH OUTPUT: 'Page Style'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line",
    ["BRAILLE LINE:  'Text Encoding $l'",
     "     VISIBLE:  'Text Encoding $l', cursor=1",
     "SPEECH OUTPUT: 'Text Encoding'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "8. Review current word",
    ["BRAILLE LINE:  'Text Encoding $l'",
     "     VISIBLE:  'Text Encoding $l', cursor=1",
     "SPEECH OUTPUT: 'Text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next word",
    ["BRAILLE LINE:  'Text Encoding $l'",
     "     VISIBLE:  'Text Encoding $l', cursor=6",
     "SPEECH OUTPUT: 'Encoding'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "10. Review current char",
    ["BRAILLE LINE:  'Text Encoding $l'",
     "     VISIBLE:  'Text Encoding $l', cursor=6",
     "SPEECH OUTPUT: 'E'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next char",
    ["BRAILLE LINE:  'Text Encoding $l'",
     "     VISIBLE:  'Text Encoding $l', cursor=7",
     "SPEECH OUTPUT: 'n'"]))

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
    ["BRAILLE LINE:  '< > Full Screen $l'",
     "     VISIBLE:  '< > Full Screen $l', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

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
    ["BRAILLE LINE:  'Text Encoding $l'",
     "     VISIBLE:  'Text Encoding $l', cursor=13",
     "SPEECH OUTPUT: 'g'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "17. Review previous word",
    ["BRAILLE LINE:  'Text Encoding $l'",
     "     VISIBLE:  'Text Encoding $l', cursor=1",
     "SPEECH OUTPUT: 'Text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "18. Review previous line",
    ["BRAILLE LINE:  'Page Style $l'",
     "     VISIBLE:  'Page Style $l', cursor=1",
     "SPEECH OUTPUT: 'Page Style'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
