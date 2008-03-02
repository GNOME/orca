#!/usr/bin/python

"""Test of Dojo tree presentation using Firefox.
"""

from macaroon.playback import *
import utils


sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dijit Tree Test" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the dojo slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "test_Tree.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dijit Tree Test", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the first tree.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to continents", 
    ["BRAILLE LINE:  'Continents ListItem'",
     "     VISIBLE:  'Continents ListItem', cursor=1",
     "BRAILLE LINE:  'Continents ListItem'",
     "     VISIBLE:  'Continents ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Continents list item expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Arrow to Africa tree item
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Africa", 
    ["BRAILLE LINE:  'Africa ListItem'",
     "     VISIBLE:  'Africa ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Africa list item collapsed'",
     "SPEECH OUTPUT: 'tree level 2'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["[[[Bug: no item # of #]]]",
     "BRAILLE LINE:  'Africa ListItem'",
     "     VISIBLE:  'Africa ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Africa'",
     "SPEECH OUTPUT: 'item 1 of 6'",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'tree level 2'"]))

########################################################################
# Use arrows to expand/collapse/navigate tree.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand Africa", 
    ["BRAILLE LINE:  'Africa ListItem'",
     "     VISIBLE:  'Africa ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Egypt", acc_role=pyatspi.ROLE_LIST_ITEM))
sequence.append(utils.AssertPresentationAction(
    "arrow to Egypt", 
    ["BRAILLE LINE:  'Egypt ListItem'",
     "     VISIBLE:  'Egypt ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Egypt list item'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Kenya", acc_role=pyatspi.ROLE_LIST_ITEM))
sequence.append(utils.AssertPresentationAction(
    "arrow to Kenya", 
    ["BRAILLE LINE:  'Kenya ListItem'",
     "     VISIBLE:  'Kenya ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Kenya list item collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand Kenya", 
    ["BRAILLE LINE:  'Kenya ListItem'",
     "     VISIBLE:  'Kenya ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "collapse Kenya", 
    ["BRAILLE LINE:  'Kenya ListItem'",
     "     VISIBLE:  'Kenya ListItem', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Sudan", 
    ["BRAILLE LINE:  'Sudan ListItem'",
     "     VISIBLE:  'Sudan ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Sudan list item collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Asia", 
    ["BRAILLE LINE:  'Asia ListItem'",
     "     VISIBLE:  'Asia ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Asia list item collapsed'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand Asia", 
    ["BRAILLE LINE:  'Asia ListItem'",
     "     VISIBLE:  'Asia ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to China", 
    ["BRAILLE LINE:  'China ListItem'",
     "     VISIBLE:  'China ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'China list item'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to India", 
    ["BRAILLE LINE:  'India ListItem'",
     "     VISIBLE:  'India ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'India list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Russia", 
    ["BRAILLE LINE:  'Russia ListItem'",
     "     VISIBLE:  'Russia ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Russia list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Mongolia", 
    ["BRAILLE LINE:  'Mongolia ListItem'",
     "     VISIBLE:  'Mongolia ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Mongolia list item'"]))
    
########################################################################
# End tree navigation
#

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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
