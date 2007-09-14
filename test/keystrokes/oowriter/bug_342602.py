#!/usr/bin/python

"""Test to verify bug #342602 is still fixed.
   StarOffice Writer - order of speaking information of table cells is incorrect.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, right arrow and Return.  (File->New->Text Document).
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", [-1, 0, 0, 0, 0], pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", [-1, 0, 0, 0, 0, 0], pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Untitled2 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3.  Enter Alt-a, right arrow and Return.  (Table->Insert->Table...).
#
sequence.append(KeyComboAction("<Alt>a"))
#sequence.append(WaitForFocus("Insert", [-1, 0, 0, 5, 0], pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Table...", [-1, 0, 0, 5, 0, 0], pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Insert Table", None))
sequence.append(WaitForFocus("Name", [-1, 1], pyatspi.ROLE_TEXT))

######################################################################
# 4. Enter Return (Insert a table with the default parameters - 2x2).
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Untitled2 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0, 0, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Enter a and Tab (Inserts "a" into cell A1 and moves to cell B1).
#
sequence.append(TypeAction("a"))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0, 1, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Enter Shift-Tab (Returns to cell A1).
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0, 0, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 7. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", [-1, 0, 0, 0, 0], pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForWindowActivate("OpenOffice.org 2.3 ", None))
sequence.append(WaitForFocus("Save", [-1, 0], pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 8. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", [3, -1, 1], pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

sequence.start()
