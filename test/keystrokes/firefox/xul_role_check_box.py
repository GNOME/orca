#!/usr/bin/python

"""Test of checkbox output using Firefox.
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

sequence.append(KeyComboAction("p"))
sequence.append(WaitForWindowActivate("Print", None))
sequence.append(PauseAction(3000))

########################################################################
# Right Arrow until we're at the Options tab 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to Page Setup",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog Page Setup Page'",
     "     VISIBLE:  'Page Setup Page', cursor=1",
     "SPEECH OUTPUT: 'Page Setup page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to Options",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog Options Page'",
     "     VISIBLE:  'Options Page', cursor=1",
     "SPEECH OUTPUT: 'Options page'"]))

########################################################################
# Tab to the Ignore Scaling and Shrink to Fit Page Width checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to checkbox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList Options Page <x> Ignore Scaling and Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '<x> Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'Ignore Scaling and Shrink To Fit Page Width check box checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList Options Page <x> Ignore Scaling and Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '<x> Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'Ignore Scaling and Shrink To Fit Page Width check box checked.'",
     "SPEECH OUTPUT: 'Alt h'"]))

########################################################################
# Toggle the state of the check box by pressing Space. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Toggle the state with space", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList Options Page < > Ignore Scaling and Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '< > Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList Options Page < > Ignore Scaling and Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '< > Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'Ignore Scaling and Shrink To Fit Page Width check box not checked.'",
     "SPEECH OUTPUT: 'Alt h'"]))

########################################################################
# Toggle the state of the check box by pressing Space. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Toggle the state with space", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Print Dialog TabList Options Page <x> Ignore Scaling and Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '<x> Ignore Scaling and Shrink To', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

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
