#!/usr/bin/python

"""Test of UIUC radio button presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "application/xhtml+xml: Radio Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/radio/view_xhtml.php?title=Radio%20Example%201&ginc=includes/radio1_xhtml.inc&gcss=css/radio1_xhtml.css&gjs=../js/globals.js,../js/widgets_xhtml.js,js/radio1_xhtml.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("application/xhtml+xml: Radio Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the first radio button group (panel).
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Lunch Options", acc_role=pyatspi.ROLE_PANEL))

########################################################################
# Move to the first radio button.
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Thai", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the second radio button.
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Subway", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the third radio button.
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Jimmy Johns", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the fourth radio button.
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Radio Maria", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the fifth radio button.
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Rainbow Gardens", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the second radio button group (panel).  Contrast to the first group
# where the "Water" radio button already has been selected.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Water", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the second radio button.
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Tea", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move back to the first radio button.
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Water", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
