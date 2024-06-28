#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to slider 1",
    ["BRAILLE LINE:  'embedded'",
     "     VISIBLE:  'embedded', cursor=1",
     "BRAILLE LINE:  '30 horizontal slider'",
     "     VISIBLE:  '30 horizontal slider', cursor=1",
     "SPEECH OUTPUT: 'horizontal slider 30.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereAmI on slider 1",
    ["BRAILLE LINE:  '30 horizontal slider'",
     "     VISIBLE:  '30 horizontal slider', cursor=1",
     "SPEECH OUTPUT: 'horizontal slider 30 30 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Increment slider 1",
    ["BRAILLE LINE:  '35 horizontal slider'",
     "     VISIBLE:  '35 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '35'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Increment slider 1",
    ["BRAILLE LINE:  '40 horizontal slider'",
     "     VISIBLE:  '40 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '40'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Decrement slider 1",
    ["BRAILLE LINE:  '35 horizontal slider'",
     "     VISIBLE:  '35 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '35'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to slider 2's left range",
    ["BRAILLE LINE:  '1950 horizontal slider'",
     "     VISIBLE:  '1950 horizontal slider', cursor=1",
     "SPEECH OUTPUT: 'horizontal slider 1950.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "7. Increment slider 2's left range",
    ["BRAILLE LINE:  '1951 horizontal slider'",
     "     VISIBLE:  '1951 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '1951'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "8. Increment slider 2's left range",
    ["BRAILLE LINE:  '1952 horizontal slider'",
     "     VISIBLE:  '1952 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '1952'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Decrement slider 2's left range",
    ["BRAILLE LINE:  '1951 horizontal slider'",
     "     VISIBLE:  '1951 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '1951'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "10. Tab to slider 2's right range",
    ["BRAILLE LINE:  '2000 horizontal slider'",
     "     VISIBLE:  '2000 horizontal slider', cursor=1",
     "SPEECH OUTPUT: 'horizontal slider 2000.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Increment slider 2's right range",
    ["BRAILLE LINE:  '2001 horizontal slider'",
     "     VISIBLE:  '2001 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '2001'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "12. Increment slider 2's right range",
    ["BRAILLE LINE:  '2002 horizontal slider'",
     "     VISIBLE:  '2002 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '2002'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Decrement slider 2's right range",
    ["BRAILLE LINE:  '2001 horizontal slider'",
     "     VISIBLE:  '2001 horizontal slider', cursor=1",
     "SPEECH OUTPUT: '2001'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
