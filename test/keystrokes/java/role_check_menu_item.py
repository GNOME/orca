#!/usr/bin/python

"""Test of check menu items in Java's SwingSet2.
"""

from macaroon.playback.keypress_mimic import *

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
sequence.append(KeyComboAction("Down"))

########################################################################
# When the first menu item "Enable Tool Tips" gets focus, the following
# should be presented in speech and braille:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swingdemo menu bar MenuBar <x> Enable Tool Tips CheckItem'
#      VISIBLE:  '<x> Enable Tool Tips CheckItem', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Enable Tool Tips check item checked'
sequence.append(WaitForFocus("Enable Tool Tips", 
                             acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Down"))

########################################################################
# When the second menu item "Enable Drag Support" gets focus, the following
# should be presented in speech and braille:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swingdemo menu bar MenuBar < > Enable Drag Support CheckItem'
#      VISIBLE:  '< > Enable Drag Support CheckIte', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Enable Drag Support check item not checked'
sequence.append(WaitForFocus("Enable Drag Support", 
                             acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# [[[Bug 483208: Exception raised when performing where am I]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: ' popup menu'
# SPEECH OUTPUT: 'Enable Drag Support'
# SPEECH OUTPUT: 'check item'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 2 of 2'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Check the menu item. Expected output:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swingdemo menu bar MenuBar <x> Enable Drag Support CheckItem'
#      VISIBLE:  '<x> Enable Drag Support CheckIte', cursor=1
# 
# SPEECH OUTPUT: 'checked'
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))

########################################################################
# Go directly back to the checked menu item, and uncheck it.

sequence.append(KeyComboAction("<Alt>p"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ROOT_PANE))
sequence.append(KeyComboAction("Down"))

########################################################################
# [[[Bug 483209: Context that appears in braille differs on same item.]]]
# Maybe because we invoked the menu with <Alt>p?
# When the second menu item "Enable Drag Support" gets focus, the following
# should be presented in speech and braille:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu <x> Enable Drag Support CheckItem'
#      VISIBLE:  '<x> Enable Drag Support CheckIte', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Enable Drag Support check item checked'

sequence.append(WaitForFocus("Enable Drag Support", 
                             acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: ' popup menu'
# SPEECH OUTPUT: 'Enable Drag Support'
# SPEECH OUTPUT: 'check item'
# SPEECH OUTPUT: 'checked'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 2 of 2'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Uncheck the menu item. Expected output:
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu < > Enable Drag Support CheckItem'
#      VISIBLE:  '< > Enable Drag Support CheckIte', cursor=1
#
# SPEECH OUTPUT: 'not checked'
sequence.append(TypeAction           (" "))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))

sequence.append(PauseAction(5000))

sequence.start()
