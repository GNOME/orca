#!/usr/bin/python

"""Test of Where am I for links."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Shift>Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Title bar",
    ["BRAILLE LINE:  'GNOME Bug Tracking System - Nightly'",
     "     VISIBLE:  'GNOME Bug Tracking System - Nigh', cursor=0",
     "SPEECH OUTPUT: 'GNOME Bug Tracking System - Nightly'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I on Product summary link", 
    ["BRAILLE LINE:  'Product summary'",
     "     VISIBLE:  'Product summary', cursor=1",
     "BRAILLE LINE:  'Product summary'",
     "     VISIBLE:  'Product summary', cursor=1",
     "SPEECH OUTPUT: 'http link Product summary.'",
     "SPEECH OUTPUT: 'different site.'"]))

# This should time out because there shouldn't be a doc load.
sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Title bar",
    ["KNOWN ISSUE: There seems to be some input event bleed through here",
     "BRAILLE LINE:  'Choose the classification - Nightly'",
     "     VISIBLE:  'Choose the classification - Nigh', cursor=0",
     "SPEECH OUTPUT: 'Choose the classification - Nightly'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Where Am I on what should be the New bug link",
    ["KNOWN ISSUE: There seems to be some input event bleed through here",
     "BRAILLE LINE:  'Home'",
     "     VISIBLE:  'Home', cursor=1",
     "BRAILLE LINE:  'Home'",
     "     VISIBLE:  'Home', cursor=1",
     "BRAILLE LINE:  'Loading.  Please wait.'",
     "     VISIBLE:  'Loading.  Please wait.', cursor=0",
     "SPEECH OUTPUT: 'https link Home.'",
     "SPEECH OUTPUT: 'same site.'",
     "SPEECH OUTPUT: 'Loading.  Please wait.' voice=system"]))


#    ["BRAILLE LINE:  'New bug'",
#     "     VISIBLE:  'New bug', cursor=1",
#     "SPEECH OUTPUT: 'http link New bug.'",
#     "SPEECH OUTPUT: 'different site.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
