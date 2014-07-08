#!/usr/bin/python

"""Test of radio menu item output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(KeyComboAction("C"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. radio menu item - not selected",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Preferences menu & y Green radio menu item(Ctrl+G)'",
     "     VISIBLE:  '& y Green radio menu item(Ctrl+G', cursor=1",
     "SPEECH OUTPUT: 'Green not selected radio menu item Ctrl+G'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. radio menu item - selected",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Preferences menu &=y Red radio menu item(Ctrl+R)'",
     "     VISIBLE:  '&=y Red radio menu item(Ctrl+R)', cursor=1",
     "SPEECH OUTPUT: 'Red selected radio menu item Ctrl+R'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
