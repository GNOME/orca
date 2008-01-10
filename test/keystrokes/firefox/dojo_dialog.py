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
# This is a kludge to ensure that the dojo widgets render properly
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dialog Widget Dojo Tests", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

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
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Launch first dialog", 
    ["BRAILLE LINE:  'First Dialog Dialog  $l'",
     "     VISIBLE:  'First Dialog Dialog  $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'First Dialog'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic whereAmI", 
    ["BRAILLE LINE:  'First Dialog Dialog  $l'",
     "     VISIBLE:  'First Dialog Dialog  $l', cursor=1",
     "SPEECH OUTPUT: 'First Dialog'",
     "SPEECH OUTPUT: 'dialog'"]))

########################################################################
# Close the dialog, focus goes back to button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "close first dialog", 
    ["BRAILLE LINE:  'Show Dialog    Button'",
     "     VISIBLE:  'Show Dialog    Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show Dialog    button'"]))

########################################################################
# Tab to the second button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to second button", 
    ["BRAILLE LINE:  'Show Tooltip Dialog Button'",
     "     VISIBLE:  'Show Tooltip Dialog Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show Tooltip Dialog button'"]))

########################################################################
# Launch the dialog  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "launch second dialog", 
    ["BRAILLE LINE:  'User:  $l'",
     "     VISIBLE:  'User:  $l', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Enter Login information User: Password:'"]))
    
########################################################################
# Close the dialog, focus goes back to button.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "close second dialog", 
    ["BRAILLE LINE:  'Show Tooltip Dialog Button'",
     "     VISIBLE:  'Show Tooltip Dialog Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show Tooltip Dialog button'"]))

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
