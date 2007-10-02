#!/usr/bin/python

"""Test of page summary
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the htmlpage.html test page.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "htmlpage.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("HTML test page", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Move to the heading level 6 so 'percent of document read' is not zero percent.
#
sequence.append(TypeAction("6"))
sequence.append(WaitForFocus("This is a Heading 6.", acc_role=pyatspi.ROLE_HEADING))

########################################################################
# Do double-click modified "Where Am I" via Orca_Modifier + KP_Enter. 
# The following should be presented in speech 
# [[[BUG? depending on the timing, the first click command still gets spoken.
# This output has been omitted here. ]]].
#
# SPEECH OUTPUT: '14 headings'
# SPEECH OUTPUT: '3 forms'
# SPEECH OUTPUT: '47 tables'
# SPEECH OUTPUT: '19 unvisited links'
# SPEECH OUTPUT: '1 percent of document read'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

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
