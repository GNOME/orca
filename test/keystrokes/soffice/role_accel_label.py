#!/usr/bin/python

"""Test of menu accelerator label output of OpenOffice.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on main window.
# This should be a blank OpenOffice.org window with no documents open.
#
sequence.append(WaitForWindowActivate("OpenOffice.org"))

########################################################################
# Now, active the "File" menu and down arrow to the "Open" menu item,
# which has an accelerator.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Open...", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Dismiss the File menu and open the Window menu, which has a 
# "Close Window" item that also has an accelerator.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(WaitForFocus("Close Window", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Dismiss everything and get us back to the place where we started.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Window", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Escape"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
