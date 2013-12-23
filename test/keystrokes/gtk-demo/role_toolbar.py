#!/usr/bin/python

"""Test of toolbar output using."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Tab"))
sequence.append(utils.AssertPresentationAction(
    "Push button initial focus",
    ["KNOWN ISSUE: The widgets on the toolbar no longer have accessible names, so Orca cannot present them.",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'tool bar push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Open triangle toggle button",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame & y Menu toggle button'",
     "     VISIBLE:  '& y Menu toggle button', cursor=1",
     "SPEECH OUTPUT: 'Menu toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Open triangle toggle button Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame & y Menu toggle button'",
     "     VISIBLE:  '& y Menu toggle button', cursor=1",
     "SPEECH OUTPUT: 'tool bar'",
     "SPEECH OUTPUT: 'Menu'",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Next push button",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame push button'",
     "     VISIBLE:  'push button', cursor=1",
     "SPEECH OUTPUT: 'tool bar push button'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
