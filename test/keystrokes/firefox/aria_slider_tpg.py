#!/usr/bin/python

"""Test of ARIA sliders using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to Volume Slider",
    ["BRAILLE LINE:  'Volume 0 % slider'",
     "     VISIBLE:  'Volume 0 % slider', cursor=1",
     "SPEECH OUTPUT: 'Volume slider 0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Volume Right Arrow",
    ["BRAILLE LINE:  'Volume 1 % slider'",
     "     VISIBLE:  'Volume 1 % slider', cursor=1",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Volume Right Arrow",
    ["BRAILLE LINE:  'Volume 2 % slider'",
     "     VISIBLE:  'Volume 2 % slider', cursor=1",
     "BRAILLE LINE:  '2 % $l'",
     "     VISIBLE:  '2 % $l', cursor=0",
     "BRAILLE LINE:  '2 % $l'",
     "     VISIBLE:  '2 % $l', cursor=0",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Volume Left Arrow",
    ["BRAILLE LINE:  'Volume 1 % slider'",
     "     VISIBLE:  'Volume 1 % slider', cursor=1",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Volume Left Arrow",
    ["BRAILLE LINE:  'Volume 0 % slider'",
     "     VISIBLE:  'Volume 0 % slider', cursor=1",
     "BRAILLE LINE:  '0 % $l'",
     "     VISIBLE:  '0 % $l', cursor=0",
     "BRAILLE LINE:  '0 % $l'",
     "     VISIBLE:  '0 % $l', cursor=0",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Volume Up Arrow",
    ["BRAILLE LINE:  'Volume 1 % slider'",
     "     VISIBLE:  'Volume 1 % slider', cursor=1",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Volume Up Arrow",
    ["BRAILLE LINE:  'Volume 2 % slider'",
     "     VISIBLE:  'Volume 2 % slider', cursor=1",
     "BRAILLE LINE:  '2 % $l'",
     "     VISIBLE:  '2 % $l', cursor=0",
     "BRAILLE LINE:  '2 % $l'",
     "     VISIBLE:  '2 % $l', cursor=0",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Volume Down Arrow",
    ["BRAILLE LINE:  'Volume 1 % slider'",
     "     VISIBLE:  'Volume 1 % slider', cursor=1",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "BRAILLE LINE:  '1 % $l'",
     "     VISIBLE:  '1 % $l', cursor=0",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Volume Down Arrow",
    ["BRAILLE LINE:  'Volume 0 % slider'",
     "     VISIBLE:  'Volume 0 % slider', cursor=1",
     "BRAILLE LINE:  '0 % $l'",
     "     VISIBLE:  '0 % $l', cursor=0",
     "BRAILLE LINE:  '0 % $l'",
     "     VISIBLE:  '0 % $l', cursor=0",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Volume Page Up",
    ["BRAILLE LINE:  'Volume 25 % slider'",
     "     VISIBLE:  'Volume 25 % slider', cursor=1",
     "BRAILLE LINE:  '25 % $l'",
     "     VISIBLE:  '25 % $l', cursor=0",
     "BRAILLE LINE:  '25 % $l'",
     "     VISIBLE:  '25 % $l', cursor=0",
     "SPEECH OUTPUT: '25 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Volume Page Down",
    ["BRAILLE LINE:  'Volume 0 % slider'",
     "     VISIBLE:  'Volume 0 % slider', cursor=1",
     "BRAILLE LINE:  '0 % $l'",
     "     VISIBLE:  '0 % $l', cursor=0",
     "BRAILLE LINE:  '0 % $l'",
     "     VISIBLE:  '0 % $l', cursor=0",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "12. Volume End",
    ["BRAILLE LINE:  'Volume 100 % slider'",
     "     VISIBLE:  'Volume 100 % slider', cursor=1",
     "BRAILLE LINE:  '100 % $l'",
     "     VISIBLE:  '100 % $l', cursor=0",
     "SPEECH OUTPUT: '100 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "13. Volume Home",
    ["BRAILLE LINE:  'Volume 0 % slider'",
     "     VISIBLE:  'Volume 0 % slider', cursor=1",
     "BRAILLE LINE:  '0 % $l'",
     "     VISIBLE:  '0 % $l', cursor=0",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "14. Tab to Food Quality Slider",
    ["KNOWN ISSUE: We're double-speaking the slider name",
     "BRAILLE LINE:  'Food Quality terrible slider'",
     "     VISIBLE:  'Food Quality terrible slider', cursor=1",
     "SPEECH OUTPUT: 'Food Quality slider terrible Food Quality: terrible (1 of 5)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "15. Food Quality Right Arrow",
    ["BRAILLE LINE:  'Food Quality bad slider'",
     "     VISIBLE:  'Food Quality bad slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "16. Food Quality Right Arrow",
    ["BRAILLE LINE:  'Food Quality decent slider'",
     "     VISIBLE:  'Food Quality decent slider', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Food Quality Left Arrow",
    ["BRAILLE LINE:  'Food Quality bad slider'",
     "     VISIBLE:  'Food Quality bad slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Food Quality Up Arrow",
    ["BRAILLE LINE:  'Food Quality decent slider'",
     "     VISIBLE:  'Food Quality decent slider', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Food Quality Down Arrow",
    ["BRAILLE LINE:  'Food Quality bad slider'",
     "     VISIBLE:  'Food Quality bad slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Food Quality Down Arrow",
    ["BRAILLE LINE:  'Food Quality terrible slider'",
     "     VISIBLE:  'Food Quality terrible slider', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Food Quality Page Up",
    ["KNOWN ISSUE: We aren't presenting this",
     "BRAILLE LINE:  'Food Quality bad slider'",
     "     VISIBLE:  'Food Quality bad slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Food Quality Page Down",
    ["KNOWN ISSUE: We aren't presenting this",
     "BRAILLE LINE:  'Food Quality terrible slider'",
     "     VISIBLE:  'Food Quality terrible slider', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "23. Food Quality End",
    ["KNOWN ISSUE: We aren't presenting this",
     "BRAILLE LINE:  'Food Quality excellent slider'",
     "     VISIBLE:  'Food Quality excellent slider', cursor=1",
     "SPEECH OUTPUT: 'excellent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "24. Food Quality Home",
    ["KNOWN ISSUE: We aren't presenting this",
     "BRAILLE LINE:  'Food Quality terrible slider'",
     "     VISIBLE:  'Food Quality terrible slider', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
