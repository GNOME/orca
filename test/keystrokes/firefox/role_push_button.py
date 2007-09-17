#!/usr/bin/python

"""Test of push button output using Firefox.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu and press U for the Page Setup dialog
#
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(WaitForFocus("New Window", pyatspi.ROLE_MENU_ITEM))
sequence.append(TypeAction("u"))

########################################################################
# In the Page Setup dialog, shift+tab to the push buttons.  Press the
# Cancel button to exit the dialog.
#
sequence.append(WaitForWindowActivate("Page Setup",None))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))

sequence.append(WaitForFocus("Format & Options", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))

sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))

sequence.append(WaitForFocus("Cancel", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction(" "))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
