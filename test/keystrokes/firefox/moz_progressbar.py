#!/usr/bin/python
# -*- coding: utf-8 -*-


"""Test of Mozilla ARIA progressbar presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "DHTML Progress Bar" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the Mozilla ARIA progressbar demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/progressbar"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("ARIA Progress Bar", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the button and press it.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to button", 
    ["BRAILLE LINE:  'Load schedule Button  Cancel Button'",
     "     VISIBLE:  'Load schedule Button  Cancel But', cursor=1",
     "SPEECH OUTPUT: 'Load schedule button'"]))

########################################################################
# Push the button to start progressbar.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))

sequence.append(utils.AssertPresentationAction(
    "progress output", 
    ["SPEECH OUTPUT: '10 percent'",
     "SPEECH OUTPUT: '20 percent'",
     "SPEECH OUTPUT: '30 percent'",
     "SPEECH OUTPUT: '40 percent'",
     "SPEECH OUTPUT: '50 percent'",
     "SPEECH OUTPUT: '60 percent'",
     "SPEECH OUTPUT: '70 percent'",
     "SPEECH OUTPUT: '80 percent'",
     "SPEECH OUTPUT: '90 percent'",
     "SPEECH OUTPUT: '100 percent'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
