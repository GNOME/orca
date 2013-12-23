#!/usr/bin/python

"""Test of toggle button output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Expander"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Toggle button Where Am I",
    ["BRAILLE LINE:  'gtk-demo application GtkExpander dialog & y Details collapsed toggle button'",
     "     VISIBLE:  '& y Details collapsed toggle but', cursor=1",
     "SPEECH OUTPUT: 'Details'",
     "SPEECH OUTPUT: 'toggle button collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Toggle button state changed to expanded",
    ["KNOWN ISSUE: Here we are presenting both the former and new state",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog &=y Details collapsed toggle button'",
     "     VISIBLE:  '&=y Details collapsed toggle but', cursor=1",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog &=y Details expanded toggle button'",
     "     VISIBLE:  '&=y Details expanded toggle butt', cursor=1",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Toggle button pressed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application GtkExpander dialog &=y Details expanded toggle button'",
     "     VISIBLE:  '&=y Details expanded toggle butt', cursor=1",
     "SPEECH OUTPUT: 'Details'",
     "SPEECH OUTPUT: 'toggle button expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Toggle button state changed to collapsed",
    ["KNOWN ISSUE: Here we are presenting both the former and new state",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog & y Details expanded toggle button'",
     "     VISIBLE:  '& y Details expanded toggle butt', cursor=1",
     "BRAILLE LINE:  'gtk-demo application GtkExpander dialog & y Details collapsed toggle button'",
     "     VISIBLE:  '& y Details collapsed toggle but', cursor=1",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
