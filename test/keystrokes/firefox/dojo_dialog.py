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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the dojo dialog demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "test_Dialog.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())


########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the show dialog button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to show dialog button", 
    ["BRAILLE LINE:  'Show Dialog Button'",
     "     VISIBLE:  'Show Dialog Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show Dialog button'"]))
     
########################################################################
# Tab to the programatic dialog button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to programatic dialog button", 
    ["BRAILLE LINE:  'Programatic Dialog (3 second delay) Button'",
     "     VISIBLE:  'Programatic Dialog (3 second del', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Programatic Dialog (3 second delay) button'"]))
     
########################################################################
# Tab to the show dialog button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to tabcontainer dialog button", 
    ["BRAILLE LINE:  'Show TabContainer Dialog Button'",
     "     VISIBLE:  'Show TabContainer Dialog Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show TabContainer Dialog button'"]))

########################################################################
# Launch the dialog  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("First tab", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "Launch dialog", 
    ["BRAILLE LINE:  'TabList First tab Page Second tab Page'",
     "     VISIBLE:  'First tab Page Second tab Page', cursor=1",
     "BRAILLE LINE:  'TabList First tab Page Second tab Page'",
     "     VISIBLE:  'First tab Page Second tab Page', cursor=1",
     "SPEECH OUTPUT: 'TabContainer Dialog dialog'",
     "SPEECH OUTPUT: 'First tab page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
# [[[Bug?: Braille output may not be correct.]]]
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic whereAmI", 
    ["BRAILLE LINE:  'TabList First tab Page Second tab Page'",
     "     VISIBLE:  'First tab Page Second tab Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'First tab page'",
     "SPEECH OUTPUT: 'item 1 of 2'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Close the dialog, focus goes back to button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Show TabContainer Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "close dialog", 
    ["BRAILLE LINE:  'Show TabContainer Dialog Button'",
     "     VISIBLE:  'Show TabContainer Dialog Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show TabContainer Dialog button'"]))

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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
