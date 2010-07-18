#!/usr/bin/python

"""Test of window title output using gtk-demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
# The following should be presented:
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, do a "Where Am I" to get the title info via
# KP_Insert+KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Window Where Am I",
    ["BRAILLE LINE:  'GTK+ Code Demos'",
     "     VISIBLE:  'GTK+ Code Demos', cursor=0",
     "SPEECH OUTPUT: 'GTK+ Code Demos'"]))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
