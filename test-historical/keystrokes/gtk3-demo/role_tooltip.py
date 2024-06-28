#!/usr/bin/python

"""Test of tooltips."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Popovers"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("<Alt>e"))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(utils.AssertPresentationAction(
    "1. Show tooltip",
    ["KNOWN ISSUE: Now that gnome-shell is used to display tooltips, the content is not accessible",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(utils.AssertPresentationAction(
    "2. Hide tooltip",
    ["BRAILLE LINE:  'gtk3-demo application Print dialog General page tab Range panel Range &=y Pages: radio button'",
     "     VISIBLE:  '&=y Pages: radio button', cursor=1",
     "SPEECH OUTPUT: 'Pages:'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
