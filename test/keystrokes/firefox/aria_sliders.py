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
    ["BRAILLE LINE:  '30 slider'",
     "     VISIBLE:  '30 slider', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'slider 30'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereAmI on slider 1",
    ["BRAILLE LINE:  '30 slider'",
     "     VISIBLE:  '30 slider', cursor=1",
     "BRAILLE LINE:  '30 slider'",
     "     VISIBLE:  '30 slider', cursor=1",
     "SPEECH OUTPUT: 'slider 30'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Increment slider 1",
    ["BRAILLE LINE:  '35 slider'",
     "     VISIBLE:  '35 slider', cursor=1",
     "SPEECH OUTPUT: '35'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Increment slider 1",
    ["BRAILLE LINE:  '40 slider'",
     "     VISIBLE:  '40 slider', cursor=1",
     "SPEECH OUTPUT: '40'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Decrement slider 1",
    ["BRAILLE LINE:  '35 slider'",
     "     VISIBLE:  '35 slider', cursor=1",
     "SPEECH OUTPUT: '35'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to slider 2's left range",
    ["BRAILLE LINE:  '1950 slider'",
     "     VISIBLE:  '1950 slider', cursor=1",
     "SPEECH OUTPUT: 'slider 1950'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "7. Increment slider 2's left range",
    ["BRAILLE LINE:  '1951 slider'",
     "     VISIBLE:  '1951 slider', cursor=1",
     "SPEECH OUTPUT: '1951'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "8. Increment slider 2's left range",
    ["BRAILLE LINE:  '1952 slider'",
     "     VISIBLE:  '1952 slider', cursor=1",
     "SPEECH OUTPUT: '1952'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Decrement slider 2's left range",
    ["BRAILLE LINE:  '1951 slider'",
     "     VISIBLE:  '1951 slider', cursor=1",
     "SPEECH OUTPUT: '1951'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "10. Tab to slider 2's right range",
    ["BRAILLE LINE:  '2000 slider'",
     "     VISIBLE:  '2000 slider', cursor=1",
     "SPEECH OUTPUT: 'slider 2000'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Increment slider 2's right range",
    ["BRAILLE LINE:  '2001 slider'",
     "     VISIBLE:  '2001 slider', cursor=1",
     "SPEECH OUTPUT: '2001'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "12. Increment slider 2's right range",
    ["BRAILLE LINE:  '2002 slider'",
     "     VISIBLE:  '2002 slider', cursor=1",
     "SPEECH OUTPUT: '2002'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Decrement slider 2's right range",
    ["BRAILLE LINE:  '2001 slider'",
     "     VISIBLE:  '2001 slider', cursor=1",
     "SPEECH OUTPUT: '2001'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
