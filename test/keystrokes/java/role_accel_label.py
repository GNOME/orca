#!/usr/bin/python

"""Test of accelerator labels in Java's SwingSet2.
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
########################################################################
# TODO: This seems to be wrong.
# When the "About" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu About'
#     VISIBLE:  'About', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'About'
# 
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("About", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
# 
# SPEECH OUTPUT: ' popup menu'
# SPEECH OUTPUT: 'About'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 1 of 5'
# SPEECH OUTPUT: ''

sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))


########################################################################
# TODO: This seems to be wrong.
# When the "Exit" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu Exit'
#      VISIBLE:  'Exit', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Exit'

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Exit", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Return SwingSet2 to begining state.
sequence.append(KeyComboAction("Escape"))

sequence.append(PauseAction(5000))

sequence.start()
