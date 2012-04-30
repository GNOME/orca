#!/usr/bin/python

"""Test of push button output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "File" menu and press P for the Print dialog
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("p"))
sequence.append(PauseAction(3000))

########################################################################
# In the Print dialog, shift+tab to move to the push button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Tab to button",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog Cancel Button'",
     "     VISIBLE:  'Cancel Button', cursor=1",
     "SPEECH OUTPUT: 'Cancel button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog Cancel Button'",
     "     VISIBLE:  'Cancel Button', cursor=1",
     "SPEECH OUTPUT: 'Cancel button.'",
     "SPEECH OUTPUT: 'Alt c'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(TypeAction("Escape"))
sequence.append(WaitForWindowActivate("", None))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
