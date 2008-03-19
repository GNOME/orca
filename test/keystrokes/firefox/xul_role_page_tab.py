#!/usr/bin/python

"""Test of page tab output using Firefox.
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
sequence.append(WaitForWindowActivate("Print",None))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Print Dialog General Page'",
     "     VISIBLE:  'General Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'General page'",
     "SPEECH OUTPUT: 'item 1 of 6'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Right Arrow to move to the second page tab.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to second page tab",
    ["BRAILLE LINE:  'Minefield Application Print Dialog Page Setup Page'",
     "     VISIBLE:  'Page Setup Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Page Setup page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Print Dialog Page Setup Page'",
     "     VISIBLE:  'Page Setup Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Page Setup page'",
     "SPEECH OUTPUT: 'item 2 of 6'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Left Arrow to move to the first page tab.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to first page tab",
    ["BRAILLE LINE:  'Minefield Application Print Dialog General Page'",
     "     VISIBLE:  'General Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'General page'"]))

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
