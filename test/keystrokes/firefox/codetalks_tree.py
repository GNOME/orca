#!/usr/bin/python

"""Test of Codetalk's tree presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Tab Panel Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://codetalks.org/source/widgets/tree/tree3.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Navigate to the first item in the tree
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to the tree",
    ["BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Foods tree'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Fruits expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Left Arrow to collapse fruits.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to collapse fruits", 
    ["BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "SPEECH OUTPUT: 'Fruits'",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Fruits'",
     "SPEECH OUTPUT: 'item 1 of 2'",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Right Arrow to expand fruits.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to expand fruits", 
    ["BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  ' Fruits $l'",
     "     VISIBLE:  ' Fruits $l', cursor=1",
     "SPEECH OUTPUT: 'Fruits'",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Fruits'",
     "SPEECH OUTPUT: 'item 1 of 2'",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

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
