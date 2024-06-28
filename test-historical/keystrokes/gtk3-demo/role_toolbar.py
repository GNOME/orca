#!/usr/bin/python

"""Test of toolbar output using."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Push button initial focus",
    ["KNOWN ISSUE: The widgets on the toolbar no longer have accessible names, so Orca cannot present them.",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'tool bar push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Open triangle toggle button",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame & y Menu toggle button'",
     "     VISIBLE:  '& y Menu toggle button', cursor=1",
     "SPEECH OUTPUT: 'Menu toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Open triangle toggle button Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame & y Menu toggle button'",
     "     VISIBLE:  '& y Menu toggle button', cursor=1",
     "SPEECH OUTPUT: 'tool bar Menu toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Next push button",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'tool bar push button'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
