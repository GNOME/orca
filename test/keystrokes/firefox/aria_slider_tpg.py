#!/usr/bin/python

"""Test of ARIA horizontal sliders using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(10000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to Volume Horizontal Slider",
    ["BRAILLE LINE:  'Volume 0 % horizontal slider'",
     "     VISIBLE:  'Volume 0 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: 'Volume horizontal slider 0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Volume Right Arrow",
    ["BRAILLE LINE:  'Volume 1 % horizontal slider'",
     "     VISIBLE:  'Volume 1 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Volume Right Arrow",
    ["BRAILLE LINE:  'Volume 2 % horizontal slider'",
     "     VISIBLE:  'Volume 2 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Volume Left Arrow",
    ["BRAILLE LINE:  'Volume 1 % horizontal slider'",
     "     VISIBLE:  'Volume 1 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Volume Left Arrow",
    ["BRAILLE LINE:  'Volume 0 % horizontal slider'",
     "     VISIBLE:  'Volume 0 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Volume Up Arrow",
    ["BRAILLE LINE:  'Volume 1 % horizontal slider'",
     "     VISIBLE:  'Volume 1 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Volume Up Arrow",
    ["BRAILLE LINE:  'Volume 2 % horizontal slider'",
     "     VISIBLE:  'Volume 2 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Volume Down Arrow",
    ["BRAILLE LINE:  'Volume 1 % horizontal slider'",
     "     VISIBLE:  'Volume 1 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Volume Down Arrow",
    ["BRAILLE LINE:  'Volume 0 % horizontal slider'",
     "     VISIBLE:  'Volume 0 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Volume Page Up",
    ["BRAILLE LINE:  'Volume 25 % horizontal slider'",
     "     VISIBLE:  'Volume 25 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '25 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Volume Page Down",
    ["BRAILLE LINE:  'Volume 0 % horizontal slider'",
     "     VISIBLE:  'Volume 0 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "12. Volume End",
    ["BRAILLE LINE:  'Volume 100 % horizontal slider'",
     "     VISIBLE:  'Volume 100 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '100 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "13. Volume Home",
    ["BRAILLE LINE:  'Volume 0 % horizontal slider'",
     "     VISIBLE:  'Volume 0 % horizontal slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "14. Tab to Food Quality Horizontal Slider",
    ["KNOWN ISSUE: The double-presentation is because of the authoring, putting the name and value into the description",
     "BRAILLE LINE:  'Food Quality terrible horizontal slider'",
     "     VISIBLE:  'Food Quality terrible horizontal', cursor=1",
     "SPEECH OUTPUT: 'Food Quality horizontal slider terrible.'",
     "SPEECH OUTPUT: 'Food Quality: terrible (1 of 5)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "15. Food Quality Right Arrow",
    ["BRAILLE LINE:  'Food Quality bad horizontal slider'",
     "     VISIBLE:  'Food Quality bad horizontal slid', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "16. Food Quality Right Arrow",
    ["BRAILLE LINE:  'Food Quality decent horizontal slider'",
     "     VISIBLE:  'Food Quality decent horizontal s', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Food Quality Left Arrow",
    ["BRAILLE LINE:  'Food Quality bad horizontal slider'",
     "     VISIBLE:  'Food Quality bad horizontal slid', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Food Quality Up Arrow",
    ["BRAILLE LINE:  'Food Quality decent horizontal slider'",
     "     VISIBLE:  'Food Quality decent horizontal s', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Food Quality Down Arrow",
    ["BRAILLE LINE:  'Food Quality bad horizontal slider'",
     "     VISIBLE:  'Food Quality bad horizontal slid', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Food Quality Down Arrow",
    ["BRAILLE LINE:  'Food Quality terrible horizontal slider'",
     "     VISIBLE:  'Food Quality terrible horizontal', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Food Quality Page Up",
    ["BRAILLE LINE:  'Food Quality bad horizontal slider'",
     "     VISIBLE:  'Food Quality bad horizontal slid', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Food Quality Page Down",
    ["BRAILLE LINE:  'Food Quality terrible horizontal slider'",
     "     VISIBLE:  'Food Quality terrible horizontal', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "23. Food Quality End",
    ["BRAILLE LINE:  'Food Quality excellent horizontal slider'",
     "     VISIBLE:  'Food Quality excellent horizonta', cursor=1",
     "SPEECH OUTPUT: 'excellent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "24. Food Quality Home",
    ["BRAILLE LINE:  'Food Quality terrible horizontal slider'",
     "     VISIBLE:  'Food Quality terrible horizontal', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
