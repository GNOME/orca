#!/usr/bin/python

"""Test of info bar output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Info bar"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

# Dismiss all the showing info bars
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("space"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("space"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("space"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("space"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("space"))

sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "1. Show the Message info bar",
    ["BRAILLE LINE:  'gtk3-demo application Info Bars frame Info bars panel &=y Message toggle button'",
     "     VISIBLE:  '&=y Message toggle button', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Info Bars frame Information info bar'",
     "     VISIBLE:  'Information info bar', cursor=1",
     "SPEECH OUTPUT: 'pressed'",
     "SPEECH OUTPUT: 'Information This is an info bar with message type GTK_MESSAGE_INFO'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Flat review the home position to read the message",
    ["BRAILLE LINE:  'This is an info bar with message type GTK_MESSAGE_INFO $l'",
     "     VISIBLE:  'This is an info bar with message', cursor=1",
     "SPEECH OUTPUT: 'This is an info bar with message type GTK_MESSAGE_INFO'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
