#!/usr/bin/python

"""Test "Where Am I" on a menu accelerator label in Firefox.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on main window.
# This should be a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu and arrow to the New Tab menu item.  Then do a
# "where am I".
#
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("New Tab", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("KP_Enter", 3000))

########################################################################
# Dismiss the menu.
#
sequence.append(KeyComboAction("Escape"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
