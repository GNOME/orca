#!/usr/bin/python

"""Test to verify spell checking support."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("The quuuiick brown fox"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("jumps overr the lazy dog"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F7"))
sequence.append(utils.AssertPresentationAction(
    "1. Enter F7 to bring up the spell checking dialog",
    ["KNOWN ISSUE: LibreOffice broke accessibility for multiline text fields so we don't present the error.",
     "SPEECH OUTPUT: 'Spelling: English (USA) frame'",
     "SPEECH OUTPUT: 'Spelling: English (USA)'",
     "SPEECH OUTPUT: 'Correct push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>I"))
sequence.append(utils.AssertPresentationAction(
    "2. Alt I to ignore the first error and present the next",
    ["KNOWN ISSUE: In addition to the above issue, we are very chatty here.",
     "SPEECH OUTPUT: 'Ignore Once push button'",
     "SPEECH OUTPUT: 'Ignore All push button'",
     "SPEECH OUTPUT: 'Add to Dictionary push button'",
     "SPEECH OUTPUT: 'Suggestions'",
     "SPEECH OUTPUT: 'quick'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
