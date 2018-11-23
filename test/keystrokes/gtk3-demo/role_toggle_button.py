#!/usr/bin/python

"""Test of toggle button output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Expander"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Toggle button Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Error alert & y Details: collapsed toggle button'",
     "     VISIBLE:  '& y Details: collapsed toggle bu', cursor=1",
     "SPEECH OUTPUT: 'Details: toggle button collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Toggle button state changed to expanded",
    ["BRAILLE LINE:  'gtk3-demo application Error alert &=y Details: expanded toggle button'",
     "     VISIBLE:  '&=y Details: expanded toggle but', cursor=1",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'Finally, the full story with all details. And all the inside information, including error codes, etc etc. Pages of information, you might have to scroll down to read it all, or even resize the window - it works !",
     "A second paragraph will contain even more innuendo, just to make you scroll down or resize the window. Do it already !' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Toggle button pressed Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Error alert &=y Details: expanded toggle button'",
     "     VISIBLE:  '&=y Details: expanded toggle but', cursor=1",
     "SPEECH OUTPUT: 'Details: toggle button expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "4. Toggle button state changed to collapsed",
    ["BRAILLE LINE:  'gtk3-demo application Error alert & y Details: collapsed toggle button'",
     "     VISIBLE:  '& y Details: collapsed toggle bu', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
