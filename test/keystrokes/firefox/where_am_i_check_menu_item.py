#!/usr/bin/python

"""Test "Where Am I" on a check menu item in Firefox.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "View" menu and Up Arrow to Full Screen.  Wait 3 seconds, then
# do a where am I.
#
sequence.append(KeyComboAction("<Alt>v"))

sequence.append(WaitForFocus("Toolbars", pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitForFocus("Full Screen", acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))
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
