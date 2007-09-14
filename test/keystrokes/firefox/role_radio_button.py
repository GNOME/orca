#!/usr/bin/python

"""Test of radio button output using Firefox.
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
# In the Page Setup dialog, focus should already be on the "Portrait"
# radio button.  Right Arrow to "Landscape" and Left Arrow back.
#
sequence.append(WaitForWindowActivate("Page Setup",None))
sequence.append(WaitForFocus("Portrait", pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Right"))

sequence.append(WaitForFocus("Landscape", pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Left"))

sequence.append(WaitForFocus("Portrait", pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Close the dialog
#
sequence.append(KeyComboAction("Escape"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus("about:blank", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
