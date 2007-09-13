#!/usr/bin/python

"""Test of checkbox output using Firefox.
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
# In the Page Setup dialog, tab to the first check box and toggle its
# state twice.
#
sequence.append(WaitForWindowActivate("Page Setup",None))
sequence.append(WaitForFocus("Portrait", pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Shrink To Fit Page Width", pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

########################################################################
# Close the dialog
#
sequence.append(KeyComboAction("Escape"))

sequence.start()
