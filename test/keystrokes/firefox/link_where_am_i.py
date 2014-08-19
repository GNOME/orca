#!/usr/bin/python

"""Test of Where am I for links."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Shift>Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Where Am I on Product summary link", 
    ["KNOWN ISSUE: This seems broken",
     "BRAILLE LINE:  '3. (designed for maintainers)Product summary'",
     "     VISIBLE:  'Product summary', cursor=1",
     "SPEECH OUTPUT: 'http link Product summary different site'"]))

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I on New bug link", 
    ["BRAILLE LINE:  'New bug · Browse · Search · Reports · Account · Admin · Help'",
     "     VISIBLE:  'New bug · Browse · Search · Repo', cursor=1",
     "SPEECH OUTPUT: 'http link New bug different site'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
