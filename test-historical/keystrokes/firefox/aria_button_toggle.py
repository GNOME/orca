#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first button",
    ["BRAILLE LINE:  '& y Font Larger toggle button'",
     "     VISIBLE:  '& y Font Larger toggle button', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",

     "SPEECH OUTPUT: 'Font Larger toggle button not pressed'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic whereamI",
    ["BRAILLE LINE:  '& y Font Larger toggle button'",
     "     VISIBLE:  '& y Font Larger toggle button', cursor=1",
     "BRAILLE LINE:  '& y Font Larger toggle button'",
     "     VISIBLE:  '& y Font Larger toggle button', cursor=1",
     "SPEECH OUTPUT: 'Font Larger toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to second button",
    ["BRAILLE LINE:  '& y Font Smaller toggle button'",
     "     VISIBLE:  '& y Font Smaller toggle button', cursor=1",
     "SPEECH OUTPUT: 'Font Smaller toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "4. Push second button",
    ["KNOWN ISSUE: We're presenting two updates.",
     "BRAILLE LINE:  '&=y Font Smaller toggle button'",
     "     VISIBLE:  '&=y Font Smaller toggle button', cursor=1",
     "BRAILLE LINE:  '& y Font Smaller toggle button'",
     "     VISIBLE:  '& y Font Smaller toggle button', cursor=1",
     "SPEECH OUTPUT: 'pressed'",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to third button",
    ["BRAILLE LINE:  '&=y Italic toggle button'",
     "     VISIBLE:  '&=y Italic toggle button', cursor=1",
     "SPEECH OUTPUT: 'Italic toggle button pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "6. Push third button",
    ["BRAILLE LINE:  '& y Italic toggle button'",
     "     VISIBLE:  '& y Italic toggle button', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab to fourth button",
    ["BRAILLE LINE:  '& y Bold toggle button'",
     "     VISIBLE:  '& y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'Bold toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "8. Push fourth button",
    ["BRAILLE LINE:  '&=y Bold toggle button'",
     "     VISIBLE:  '&=y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "9. Push fourth button again",
    ["BRAILLE LINE:  '& y Bold toggle button'",
     "     VISIBLE:  '& y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
