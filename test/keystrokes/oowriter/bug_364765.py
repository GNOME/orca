#!/usr/bin/python

"""Test to verify bug #364765 is still fixed.
   Escaping out of Wizards submenu in OOo Writer causes Orca to report 
   "Format menu".
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, to display the File menu.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

######################################################################
# 3. Press W to open the Wizards submenu.
#
sequence.append(TypeAction("w"))
sequence.append(WaitForFocus("Letter...", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 4. Press Escape to close the Wizards submenu.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Wizards", acc_role=pyatspi.ROLE_MENU))

######################################################################
# 5. Press Escape to close the File submenu.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))

sequence.start()
