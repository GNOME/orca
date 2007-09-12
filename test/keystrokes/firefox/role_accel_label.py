#!/usr/bin/python

"""Test of menu accelerator label output of Firefox.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on main window.
# This should be a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu and arrow down through the menu items.  When
# done, press Escape to close the menu and return Firefox to the
# state where we started.
#
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("New Tab", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Open Location...", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Open File...", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Close", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Save Page As...", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Send Link...", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Escape"))

sequence.start()
