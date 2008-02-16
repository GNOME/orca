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
    "Tab to show dialog", 
    ["BRAILLE LINE:  'Show Dialog    Button'",
     "     VISIBLE:  'Show Dialog    Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show Dialog    button'"]))

########################################################################
# Launch the dialog  
#
# [[[Bug?: Braille output may not be correct.]]]
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Name:", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Launch first dialog", 
    ["BRAILLE LINE:  'Name: Name:   $l'",
     "     VISIBLE:  'Name: Name:   $l', cursor=14",
     "SPEECH OUTPUT: 'First Dialog dialog'",
     "SPEECH OUTPUT: 'Name:  text '"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
# [[[Bug?: Braille output may not be correct.]]]
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic whereAmI", 
    ["BRAILLE LINE:  'Name: Name:   $l'",
     "     VISIBLE:  'Name: Name:   $l', cursor=14",
     "SPEECH OUTPUT: 'Name:  Name:'",
     "SPEECH OUTPUT: 'text'"]))

########################################################################
# Close the dialog, focus goes back to button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Show Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "close first dialog", 
    ["BRAILLE LINE:  'Show Dialog    Button'",
     "     VISIBLE:  'Show Dialog    Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show Dialog    button'"]))

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
