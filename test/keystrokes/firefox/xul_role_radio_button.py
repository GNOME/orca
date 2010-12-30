#!/usr/bin/python

"""Test of radio button output using Firefox.
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
# Press Alt A to jump to the radio button group
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>a"))
sequence.append(utils.AssertPresentationAction(
    "Alt a to radio button group",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList General Page Range &=y All Pages RadioButton'",
     "     VISIBLE:  '&=y All Pages RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Range All Pages selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList General Page Range &=y All Pages RadioButton'",
     "     VISIBLE:  '&=y All Pages RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Range All Pages radio button selected 1 of 4.'",
     "SPEECH OUTPUT: 'Alt a'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
