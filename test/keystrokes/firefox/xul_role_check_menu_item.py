#!/usr/bin/python

"""Test of menu checkbox output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "View" menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(utils.AssertPresentationAction(
    "View menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar View Menu'",
     "     VISIBLE:  'View Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Toolbars Menu'",
     "     VISIBLE:  'Toolbars Menu', cursor=1",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Toolbars menu'"]))

########################################################################
# When focus is on Toolbars, Up Arrow to the "Full Screen" check menu
# item. The following should be presented in speech and braille:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in View menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar < > Full Screen CheckItem\(F11\)'",
     "     VISIBLE:  '< > Full Screen CheckItem(F11)', cursor=1",
     "SPEECH OUTPUT: 'Full Screen check item not checked F11'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar < > Full Screen CheckItem\(F11\)'",
     "     VISIBLE:  '< > Full Screen CheckItem(F11)', cursor=1",
     "SPEECH OUTPUT: 'tool bar View menu Full Screen check item not checked F11 10 of 10.'",
     "SPEECH OUTPUT: 'F'"]))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
