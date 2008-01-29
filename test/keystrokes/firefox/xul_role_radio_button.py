#!/usr/bin/python

"""Test of radio button output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield", None))

########################################################################
# Open the "File" menu and press P for the Print dialog
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(KeyComboAction("p"))

########################################################################
# Press Alt A to jump to the radio button group
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>a"))
sequence.append(utils.AssertPresentationAction(
    "Alt a to radio button group",
    ["BRAILLE LINE:  'Minefield Application Print Dialog TabList General Page Print Pages Filler &=y All RadioButton'",
     "     VISIBLE:  '&=y All RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Print Pages'",
     "SPEECH OUTPUT: 'All selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Print Dialog TabList General Page Print Pages Filler &=y All RadioButton'",
     "     VISIBLE:  '&=y All RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Print Pages'",
     "SPEECH OUTPUT: 'All radio button'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'item 1 of 3'",
     "SPEECH OUTPUT: 'Alt a'"]))

########################################################################
# Down Arrow to the next radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow to next radio button",
    ["BRAILLE LINE:  'Minefield Application Print Dialog TabList General Page Print Pages Filler & y Range RadioButton'",
     "     VISIBLE:  '& y Range RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Range not selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Print Dialog TabList General Page Print Pages Filler &=y Range RadioButton'",
     "     VISIBLE:  '&=y Range RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Print Pages'",
     "SPEECH OUTPUT: 'Range radio button'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'item 3 of 3'",
     "SPEECH OUTPUT: 'Alt n'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
