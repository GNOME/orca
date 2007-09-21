#!/usr/bin/python

"""Test of Mozilla ARIA progressbar presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "DHTML Progress Bar" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA progressbar demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/progressbar"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("DHTML Progress Bar", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the button and press it.  This starts the progressbar.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Load schedule", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

########################################################################
# Wait for the table to pop up indicating that the task is done.  Note:
# other events such as object:children-changed:add on document frame did
# not work here.
#
sequence.append(WaitAction("object:property-change:accessible-parent",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           15000))

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
