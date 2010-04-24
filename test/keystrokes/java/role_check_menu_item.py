#!/usr/bin/python

"""Test of check menu items in Java's SwingSet2.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

sequence.append(PauseAction(5000))

sequence.append(KeyComboAction("F10"))
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Look & Feel", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Themes", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Options", acc_role=pyatspi.ROLE_MENU))

########################################################################
# Go Down to the Enable Tool Tips menu item
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Enable Tool Tips", 
                             acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "Enable Tool Tips checked check menu item",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar <x> Enable Tool Tips CheckBox'",
     "     VISIBLE:  '<x> Enable Tool Tips CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Enable Tool Tips check box checked'"]))

########################################################################
# Go Down to the Enable Drag Support menu item
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Enable Drag Support", 
                             acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "Enable Drag Support unchecked menu item",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar < > Enable Drag Support CheckBox'",
     "     VISIBLE:  '< > Enable Drag Support CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Enable Drag Support check box not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Enable Drag Support unchecked menu item Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar < > Enable Drag Support CheckBox'",
     "     VISIBLE:  '< > Enable Drag Support CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Enable Drag Support check box not checked.'",
     "SPEECH OUTPUT: 'D'",
     "SPEECH OUTPUT: 'Enable or disable drag support'"]))

########################################################################
# Check the menu item.
# 
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))

########################################################################
# Go directly back to the checked menu item.
#
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Enable Drag Support", 
                             acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "Enable Drag Support checked menu item",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar <x> Enable Drag Support CheckBox'",
     "     VISIBLE:  '<x> Enable Drag Support CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Enable Drag Support check box checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Enable Drag Support checked menu item Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar <x> Enable Drag Support CheckBox'",
     "     VISIBLE:  '<x> Enable Drag Support CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Enable Drag Support check box checked.'",
     "SPEECH OUTPUT: 'D'",
     "SPEECH OUTPUT: 'Enable or disable drag support'"]))

########################################################################
# Uncheck the menu item.
#
sequence.append(TypeAction(" "))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
