#!/usr/bin/python

"""Test presentation of character attributes."""

from macaroon.playback import *

sequence = MacroSequence()
import utils

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>b"))
sequence.append(TypeAction("Bold"))
sequence.append(KeyComboAction("<Control>b"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("<Control>i"))
sequence.append(TypeAction("Italic"))
sequence.append(KeyComboAction("<Control>i"))
sequence.append(TypeAction(" Normal"))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Font information for bold word",
    ["SPEECH OUTPUT: 'size: 12' voice=system",
     "SPEECH OUTPUT: 'family name: Liberation Serif' voice=system",
     "SPEECH OUTPUT: 'bold' voice=system",
     "SPEECH OUTPUT: 'paragraph style: Default Style' voice=system",
     "SPEECH OUTPUT: 'foreground color: black' voice=system",
     "SPEECH OUTPUT: 'background color: white' voice=system"]))

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Font information for italic word",
    ["SPEECH OUTPUT: 'size: 12' voice=system",
     "SPEECH OUTPUT: 'family name: Liberation Serif' voice=system",
     "SPEECH OUTPUT: 'style: italic' voice=system",
     "SPEECH OUTPUT: 'paragraph style: Default Style' voice=system",
     "SPEECH OUTPUT: 'foreground color: black' voice=system",
     "SPEECH OUTPUT: 'background color: white' voice=system"]))

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Font information for regular word",
    ["SPEECH OUTPUT: 'size: 12' voice=system",
     "SPEECH OUTPUT: 'family name: Liberation Serif' voice=system",
     "SPEECH OUTPUT: 'paragraph style: Default Style' voice=system",
     "SPEECH OUTPUT: 'foreground color: black' voice=system",
     "SPEECH OUTPUT: 'background color: white' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
