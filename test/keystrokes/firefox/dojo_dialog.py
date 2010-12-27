#!/usr/bin/python

"""Test of Dojo dialog presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dialog Widget Dojo Test" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo dialog demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "test_Dialog.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())


########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(6000))

########################################################################
# Tab to the show dialog button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to show dialog button", 
    ["BUG? - Why no braille here and on several other buttons?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'Show Dialog button'"]))
     
########################################################################
# Tab to the programatic dialog button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to programatic dialog button", 
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'Programatic Dialog \(3 second delay\) button'"]))
     
########################################################################
# Tab to the show dialog button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to tabcontainer dialog button", 
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'Show TabContainer Dialog button'"]))

########################################################################
# Launch the dialog  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("First tab", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "Launch dialog", 
    ["BRAILLE LINE:  ' First tab  Second tab'",
     "     VISIBLE:  ' First tab  Second tab', cursor=0",
     "SPEECH OUTPUT: 'TabContainer Dialog dialog First tab page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
# [[[Bug?: Braille output may not be correct.]]]
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic whereAmI", 
    ["BRAILLE LINE:  ' First tab  Second tab'",
     "     VISIBLE:  ' First tab  Second tab', cursor=0",
     "SPEECH OUTPUT: 'tab list First tab page 1 of 2'"]))

########################################################################
# Close the dialog, focus goes back to button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Show TabContainer Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "close dialog", 
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'Show TabContainer Dialog button'"]))

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
