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

sequence.append(PauseAction(5000))

########################################################################
# Navigate to the first item in the tree
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to the tree",
    ["BUG? - Why the double braille? 4.0 issue??",
     "BRAILLE LINE:  'Fruits Fruits expanded ListItem'",
     "     VISIBLE:  'Fruits Fruits expanded ListItem', cursor=1",
     "SPEECH OUTPUT: 'Foods tree Fruits expanded tree level 1'"]))

########################################################################
# Left Arrow to collapse fruits.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to collapse fruits", 
    ["BRAILLE LINE:  'Fruits Fruits collapsed ListItem'",
     "     VISIBLE:  'Fruits Fruits collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Fruits Fruits collapsed ListItem'",
     "     VISIBLE:  'Fruits Fruits collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'Fruits list item Fruits 1 of 2 collapsed tree level 1'"]))

########################################################################
# Right Arrow to expand fruits.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to expand fruits", 
    ["BRAILLE LINE:  'Fruits Fruits expanded ListItem'",
     "     VISIBLE:  'Fruits Fruits expanded ListItem', cursor=1",
     "BRAILLE LINE:  'Fruits Fruits expanded ListItem'",
     "     VISIBLE:  'Fruits Fruits expanded ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Fruits Fruits expanded ListItem'",
     "     VISIBLE:  'Fruits Fruits expanded ListItem', cursor=1",
     "SPEECH OUTPUT: 'Fruits list item Fruits 1 of 2 expanded tree level 1'"]))

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
