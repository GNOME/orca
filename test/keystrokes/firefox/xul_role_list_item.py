#!/usr/bin/python

"""Test of list item output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "Edit" menu and Up Arrow to Preferences, then press Return.
#
sequence.append(KeyComboAction("<Alt>e"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Minefield Preferences",None))

########################################################################
# Press Right Arrow to move forward list item by list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow in list",
    ["BRAILLE LINE:  'Minefield Application Minefield Preferences Frame List Tabs ListItem'",
     "     VISIBLE:  'Tabs ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tabs'",
     "SPEECH OUTPUT: 'New pages should be opened in:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow in list",
    ["BRAILLE LINE:  'Minefield Application Minefield Preferences Frame List Content ListItem'",
     "     VISIBLE:  'Content ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Content'",
     "SPEECH OUTPUT: 'Size:'",
     "SPEECH OUTPUT: 'Default font:'"]))

########################################################################
# Press Left Arrow to move backward list item by list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow in list",
    ["BRAILLE LINE:  'Minefield Application Minefield Preferences Frame List Tabs ListItem'",
     "     VISIBLE:  'Tabs ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tabs'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow in list",
    ["BRAILLE LINE:  'Minefield Application Minefield Preferences Frame List Main ListItem'",
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
    ["BRAILLE LINE:  'Minefield Application Minefield Preferences Frame List Main ListItem'",
     "     VISIBLE:  'Main ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Main'",
     "SPEECH OUTPUT: 'item 1 of 7'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
