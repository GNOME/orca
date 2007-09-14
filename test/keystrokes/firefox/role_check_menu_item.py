#!/usr/bin/python

"""Test of menu checkbox output using Firefox.
"""
from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "View" menu and Up Arrow to Full Screen.
#
sequence.append(KeyComboAction("<Alt>v"))

sequence.append(WaitForFocus("Toolbars", pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitForFocus("Full Screen", acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))

########################################################################
# Dismiss the menu.
#
sequence.append(KeyComboAction("Escape"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus("Minefield", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
