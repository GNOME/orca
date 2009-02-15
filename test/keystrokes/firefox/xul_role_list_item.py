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
sequence.append(WaitForWindowActivate("",None))
sequence.append(PauseAction(3000))

########################################################################
# Press Right Arrow to get to the next list item and Left Arrow to
# get back. We'll do this because in Firefox 3.1 we are not getting the
# correct events until we Alt+Tab out of and then back into the window.
# This does not seem to be an issue for Firefox 3.0
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow in list",
    ["KNOWN ISSUE - Firefox 3.1 is not giving us anything here, but Firefox 3.0 is. If we have output, the bug is not present."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow in list",
    ["KNOWN ISSUE - Firefox 3.1 is not giving us anything here, but Firefox 3.0 is. If we have output, the bug is not present."]))

sequence.append(KeyComboAction("<Alt>Tab"))
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))
sequence.append(KeyComboAction("<Alt>Tab"))
sequence.append(WaitForWindowActivate(utils.firefoxAppNames + " Preferences", None))

########################################################################
# Press Right Arrow to move forward list item by list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow in list",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List Tabs ListItem'",
     "     VISIBLE:  'Tabs ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tabs'"]))

########################################################################
# Press Left Arrow to move backward list item by list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow in list",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List Main ListItem'",
     "     VISIBLE:  'Main ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Main'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List Main ListItem'",
     "     VISIBLE:  'Main ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Main'",
     "SPEECH OUTPUT: 'item 1 of 7'"]))

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
