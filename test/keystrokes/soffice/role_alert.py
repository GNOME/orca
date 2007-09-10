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
# Now, press Ctrl+n to create a new writer document and type "test" in
# it.
#
sequence.append(KeyComboAction("<Control>n"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ROOT_PANE))
sequence.append(TypeAction("test", 500))

########################################################################
# Press Ctrl+w to close the window.  This should pop up an alert which
# Orca should automatically read.  Arrow to the "Discard" button and
# dismiss the dialog to get us back where we started.
#
sequence.append(KeyComboAction("<Control>w"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
