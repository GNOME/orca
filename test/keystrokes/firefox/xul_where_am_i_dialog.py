# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of where Am I output in a dialog box using Firefox.
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
# Read the title bar with Orca+KP_ENTER
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Title Bar", 
    ["BRAILLE LINE:  'Print'",
     "     VISIBLE:  'Print', cursor=0",
     "SPEECH OUTPUT: 'Print'"]))

########################################################################
# Tab once to select an option so that the default button will be
# available.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

########################################################################
# Obtain the default button with Orca+KP_ENTER double clicked.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Default button", 
    ["BRAILLE LINE:  'Print'",
     "     VISIBLE:  'Print', cursor=0",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList General Page ScrollPane Table'",
     "     VISIBLE:  'Table', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList General Page ScrollPane Table'",
     "     VISIBLE:  'Table', cursor=1",
     "BRAILLE LINE:  'Default button is Print'",
     "     VISIBLE:  'Default button is Print', cursor=0",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList General Page ScrollPane Table  Print to File  '",
     "     VISIBLE:  ' Print to File  ', cursor=1",
     "SPEECH OUTPUT: 'Print'",
     "SPEECH OUTPUT: 'Default button is Print'",
     "SPEECH OUTPUT: 'image Print to File'"]))

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
