#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(3000))
sequence.append(TypeAction("cd "))

slash = utils.getKeyCodeForName("slash")
sequence.append(KeyPressAction(0, slash, None))
sequence.append(KeyReleaseAction(0, slash, None))

sequence.append(TypeAction("ho"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to complete 'cd /ho'",
    []))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
