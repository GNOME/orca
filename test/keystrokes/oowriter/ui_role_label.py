#!/usr/bin/python

"""Test to verify presentation of focusable labels."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Alt>f"))
sequence.append(TypeAction("w"))
sequence.append(TypeAction("a"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down arrow to the first item",
    ["BRAILLE LINE:  'soffice application Agenda Wizard frame Agenda Wizard dialog Steps panel General information'",
     "     VISIBLE:  ' General information', cursor=1",
     "SPEECH OUTPUT: 'Agenda Wizard Please choose the page design for the agenda Page design: This wizard helps you to create an agenda template. The template can then be used to create an agenda whenever needed.'",
     "SPEECH OUTPUT: 'Steps panel'",
     "SPEECH OUTPUT: 'General information'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down arrow to the next item",
    ["BRAILLE LINE:  'soffice application Agenda Wizard frame Agenda Wizard dialog Steps panel Headings to include'",
     "     VISIBLE:  ' Headings to include', cursor=1",
     "SPEECH OUTPUT: 'Headings to include'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
