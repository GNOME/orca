#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to link",
    ["BRAILLE LINE:  'Display a dialog'",
     "     VISIBLE:  'Display a dialog', cursor=1",
     "SPEECH OUTPUT: 'Display a dialog link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Return to open dialog",
    ["BRAILLE LINE:  'Just an example. dialog'",
     "     VISIBLE:  'Just an example. dialog', cursor=1",
     "SPEECH OUTPUT: 'Just an example.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to dialog button",
    ["BRAILLE LINE:  'OK push button'",
     "     VISIBLE:  'OK push button', cursor=1",
     "SPEECH OUTPUT: 'OK push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "4. Escape to dismiss dialog",
    ["KNOWN ISSUE: https://bugzilla.mozilla.org/show_bug.cgi?id=1190882",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down to move to next line",
    ["KNOWN ISSUE: https://bugzilla.mozilla.org/show_bug.cgi?id=1190882",
     ""]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
