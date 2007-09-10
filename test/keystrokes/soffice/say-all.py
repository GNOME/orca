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
# We depend upon the harness to read say-all.params and tell soffice to
# open the text/SayAllText.txt file for us.  Once that is open, do a
# SayAll.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(KeyComboAction("KP_Add"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=10000))

########################################################################
# Press Ctrl+w to close the window.  This should get us back where we
# started.
#
sequence.append(KeyComboAction("<Control>w"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
