#!/usr/bin/python

"""Test of gtk+ checkbox output from within Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(KeyComboAction("p"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Right Arrow to Page Setup",
    ["BRAILLE LINE:  'Firefox application Print dialog Page Setup page tab'",
     "     VISIBLE:  'Page Setup page tab', cursor=1",
     "SPEECH OUTPUT: 'Page Setup page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right Arrow to Options",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab'",
     "     VISIBLE:  'Options page tab', cursor=1",
     "SPEECH OUTPUT: 'Options page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to checkbox",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab <x> Ignore Scaling and Shrink To Fit Page Width check box'",
     "     VISIBLE:  '<x> Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'Ignore Scaling and Shrink To Fit Page Width check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab <x> Ignore Scaling and Shrink To Fit Page Width check box'",
     "     VISIBLE:  '<x> Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'Ignore Scaling and Shrink To Fit Page Width check box checked.'",
     "SPEECH OUTPUT: 'Alt+H'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "5. Toggle the state with space",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab < > Ignore Scaling and Shrink To Fit Page Width check box'",
     "     VISIBLE:  '< > Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab < > Ignore Scaling and Shrink To Fit Page Width check box'",
     "     VISIBLE:  '< > Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'Ignore Scaling and Shrink To Fit Page Width check box not checked.'",
     "SPEECH OUTPUT: 'Alt+H'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "7. Toggle the state with space",
    ["BRAILLE LINE:  'Firefox application Print dialog Options page tab <x> Ignore Scaling and Shrink To Fit Page Width check box'",
     "     VISIBLE:  '<x> Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
