#!/usr/bin/python

"""Test of Mozilla ARIA checkbox presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "DHTML Checkbox" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA checkbox demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/checkbox"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("DHTML Checkbox", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the first checkbox and uncheck it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Include decorative fruit basket", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

########################################################################
# Tab to the second checkbox and uncheck it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Required checkbox", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

########################################################################
# Tab to the third checkbox and uncheck it then check it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Invalid checkbox", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))
sequence.append(TypeAction(" "))

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
