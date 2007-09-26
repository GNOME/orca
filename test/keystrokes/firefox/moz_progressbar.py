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
# Tab to the button and press it.  The following will be presented.
# Note: unicode chars removed from between 'schedule' and 'Cancel'
#
#  BRAILLE LINE:  'Load schedule   Cancel'
#       VISIBLE:  'Load schedule   Cancel', cursor=0
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Load schedule button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Load schedule", acc_role=pyatspi.ROLE_PUSH_BUTTON))



########################################################################
# Push the button to start progressbar.  The following will be presented
# on each update.
# [[[Bug?: no Braille output]]]
#
sequence.append(KeyComboAction("Return"))

# SPEECH OUTPUT: '5 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '10 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '15 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '20 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '25 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '30 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '35 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '40 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '45 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '50 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '55 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '60 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '65 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '70 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '75 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '80 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '85 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '90 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '95 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
# SPEECH OUTPUT: '100 percent. '
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))

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
