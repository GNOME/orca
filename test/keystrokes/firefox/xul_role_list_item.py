#!/usr/bin/python

"""Test of list item output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "Edit" menu and Up Arrow to Preferences, then press Return.
#
sequence.append(KeyComboAction("<Alt>e"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("", None))
sequence.append(PauseAction(3000))

########################################################################
# Press Right Arrow to move forward list item by list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow in list",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List Tabs ListItem'",
     "     VISIBLE:  'Tabs ListItem', cursor=1",
     "SPEECH OUTPUT: 'Tabs'"]))

########################################################################
# Press Left Arrow to move backward list item by list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow in list",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List General ListItem'",
     "     VISIBLE:  'General ListItem', cursor=1",
     "SPEECH OUTPUT: 'General'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List General ListItem'",
     "     VISIBLE:  'General ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item General 1 of 8'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
