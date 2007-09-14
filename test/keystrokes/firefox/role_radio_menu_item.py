#!/usr/bin/python

"""Test of menu radio button output using Firefox.
"""
from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "View" menu and press Y for the "Page Style" menu.  Then
# arrow to each of the two items.
#
sequence.append(KeyComboAction("<Alt>v"))

sequence.append(WaitForFocus("Toolbars", pyatspi.ROLE_MENU))
sequence.append(TypeAction("y"))

sequence.append(WaitForFocus("No Style", pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Basic Page Style", pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitForFocus("No Style", pyatspi.ROLE_RADIO_MENU_ITEM))

########################################################################
# Dismiss the "Page Style" menu and then the "View" menu.
#
sequence.append(KeyComboAction("Escape"))

sequence.append(WaitForFocus("Page Style", pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Escape"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus("about:blank", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
