#!/usr/bin/python

"""Test of UIUC button presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "text/html: Button Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/button/html.php?title=Button%20Example%201&ginc=includes/button1.inc&gcss=css/button1.css&gjs=../js/globals.js,../js/enable_app.js,js/button1.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("text/html: Button Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the first button and push it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Reduce Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Tab to the second button and push it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Enlarge Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Tab to the third button and push it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Italicize Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Tab to the fourth button and push it twice.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Bold Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction           ("  "))
sequence.append(TypeAction           ("  "))

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
