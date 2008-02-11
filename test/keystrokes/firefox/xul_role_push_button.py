#!/usr/bin/python

"""Test of push button output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu and press P for the Print dialog
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(KeyComboAction("p"))
sequence.append(PauseAction(3000))

########################################################################
# In the Print dialog, shift+tab to move to the push button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Tab to button",
    ["BRAILLE LINE:  'Minefield Application Print Dialog Print Button'",
     "     VISIBLE:  'Print Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Print button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Print Dialog Print Button'",
     "     VISIBLE:  'Print Button', cursor=1",
     "SPEECH OUTPUT: 'Print'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: 'Alt p'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(TypeAction("Escape"))
sequence.append(WaitForWindowActivate("Minefield",None))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
