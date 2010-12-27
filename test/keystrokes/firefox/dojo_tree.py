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
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "tree/test_Tree.html"))
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
    ["BRAILLE LINE:  'Continents expanded ListItem'",
     "     VISIBLE:  'Continents expanded ListItem', cursor=1",
     "SPEECH OUTPUT: 'Continents expanded tree level 1'"]))

########################################################################
# Arrow to Africa tree item
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Africa", 
    ["BRAILLE LINE:  'Africa collapsed ListItem'",
     "     VISIBLE:  'Africa collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'Africa collapsed tree level 2'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Africa collapsed ListItem'",
     "     VISIBLE:  'Africa collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item Africa 1 of 6 collapsed tree level 2'"]))

########################################################################
# Use arrows to expand/collapse/navigate tree.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand Africa", 
    ["BRAILLE LINE:  'Africa expanded ListItem'",
     "     VISIBLE:  'Africa expanded ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Egypt", acc_role=pyatspi.ROLE_LIST_ITEM))
sequence.append(utils.AssertPresentationAction(
    "arrow to Egypt", 
    ["BRAILLE LINE:  'Egypt ListItem'",
     "     VISIBLE:  'Egypt ListItem', cursor=1",
     "SPEECH OUTPUT: 'Egypt tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Kenya", acc_role=pyatspi.ROLE_LIST_ITEM))
sequence.append(utils.AssertPresentationAction(
    "arrow to Kenya", 
    ["BRAILLE LINE:  'Kenya collapsed ListItem'",
     "     VISIBLE:  'Kenya collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'Kenya collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand Kenya", 
    ["BRAILLE LINE:  'Kenya expanded ListItem'",
     "     VISIBLE:  'Kenya expanded ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "collapse Kenya", 
    ["BRAILLE LINE:  'Kenya collapsed ListItem'",
     "     VISIBLE:  'Kenya collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Sudan", 
    ["BRAILLE LINE:  'Sudan collapsed ListItem'",
     "     VISIBLE:  'Sudan collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'Sudan collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Asia", 
    ["BRAILLE LINE:  'Asia collapsed ListItem'",
     "     VISIBLE:  'Asia collapsed ListItem', cursor=1",
     "SPEECH OUTPUT: 'Asia collapsed tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand Asia", 
    ["BRAILLE LINE:  'Asia expanded ListItem'",
     "     VISIBLE:  'Asia expanded ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to China", 
    ["BRAILLE LINE:  'China ListItem'",
     "     VISIBLE:  'China ListItem', cursor=1",
     "SPEECH OUTPUT: 'China tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to India", 
    ["BRAILLE LINE:  'India ListItem'",
     "     VISIBLE:  'India ListItem', cursor=1",
     "SPEECH OUTPUT: 'India'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Russia", 
    ["BRAILLE LINE:  'Russia ListItem'",
     "     VISIBLE:  'Russia ListItem', cursor=1",
     "SPEECH OUTPUT: 'Russia'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to Mongolia", 
    ["BRAILLE LINE:  'Mongolia ListItem'",
     "     VISIBLE:  'Mongolia ListItem', cursor=1",
     "SPEECH OUTPUT: 'Mongolia'"]))
    
########################################################################
# End tree navigation
#

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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
