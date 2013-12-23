#!/usr/bin/python

"""Test of info bar output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Info bar"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Start the demo",
    ["BRAILLE LINE:  'gtk-demo application Info Bars frame'",
     "     VISIBLE:  'Info Bars frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Info Bars frame Question info bar OK push button'",
     "     VISIBLE:  'OK push button', cursor=1",
     "SPEECH OUTPUT: 'Info Bars frame'",
     "SPEECH OUTPUT: 'Question This is",
     "an info bar with message type",
     "GTK_MESSAGE_QUESTION'",
     "SPEECH OUTPUT: 'OK push button'"]))

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
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "Show the Message info bar",
    ["BRAILLE LINE:  'gtk-demo application Info Bars frame Info bars panel An example of different info bars filler &=y Message toggle button'",
     "     VISIBLE:  '&=y Message toggle button', cursor=1",
     "SPEECH OUTPUT: 'pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Flat review the home position to read the message",
    ["BRAILLE LINE:  'This is an info bar with message type GTK_MESSAGE_INFO filler $l'",
     "     VISIBLE:  'This is an info bar with message', cursor=1",
     "SPEECH OUTPUT: 'This is an info bar with message type GTK_MESSAGE_INFO filler'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
