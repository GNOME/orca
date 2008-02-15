#!/usr/bin/python

"""Test of UIUC tree presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Tree Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/tree/view_inline.php?title=Tree%20Example%201&ginc=includes/tree1_inline.inc&gcss=css/tree1_inline.css&gjs=../js/globals.js,../js/widgets_inline.js,js/tree1_inline.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("inline: Tree Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the tree.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Fruits", acc_role=pyatspi.ROLE_LIST_ITEM))
sequence.append(utils.AssertPresentationAction(
    "tab to tree", 
    ["BRAILLE LINE:  'Fruits ListItem'",
     "     VISIBLE:  'Fruits ListItem', cursor=1",
     "BRAILLE LINE:  'Fruits ListItem'",
     "     VISIBLE:  'Fruits ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Foods tree'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Fruits list item expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Fruits ListItem'",
     "     VISIBLE:  'Fruits ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Fruits'",
     "SPEECH OUTPUT: 'item 1 of 2'",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Navigate the tree using the arrows.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to oranges", 
    ["BRAILLE LINE:  'Oranges ListItem'",
     "     VISIBLE:  'Oranges ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Oranges list item'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to pineapples", 
    ["BRAILLE LINE:  'Pineapples ListItem'",
     "     VISIBLE:  'Pineapples ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Pineapples list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to apples", 
    ["BRAILLE LINE:  'Apples ListItem'",
     "     VISIBLE:  'Apples ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Apples list item collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand apples", 
    ["BRAILLE LINE:  'Apples ListItem'",
     "     VISIBLE:  'Apples ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to macintosh", 
    ["BRAILLE LINE:  'Macintosh ListItem'",
     "     VISIBLE:  'Macintosh ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Macintosh list item'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to granny smith", 
    ["BRAILLE LINE:  'Granny Smith ListItem'",
     "     VISIBLE:  'Granny Smith ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Granny Smith list item collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "expand granny smith", 
    ["BRAILLE LINE:  'Granny Smith ListItem'",
     "     VISIBLE:  'Granny Smith ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to washington state", 
    ["BRAILLE LINE:  'Washington State ListItem'",
     "     VISIBLE:  'Washington State ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Washington State list item'",
     "SPEECH OUTPUT: 'tree level 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to michigan", 
    ["BRAILLE LINE:  'Michigan ListItem'",
     "     VISIBLE:  'Michigan ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Michigan list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to new york", 
    ["BRAILLE LINE:  'New York ListItem'",
     "     VISIBLE:  'New York ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'New York list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to fuji", 
    ["BRAILLE LINE:  'Fuji ListItem'",
     "     VISIBLE:  'Fuji ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Fuji list item'",
     "SPEECH OUTPUT: 'tree level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to bananas", 
    ["BRAILLE LINE:  'Bananas ListItem'",
     "     VISIBLE:  'Bananas ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bananas list item'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to pears", 
    ["BRAILLE LINE:  'Pears ListItem'",
     "     VISIBLE:  'Pears ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Pears list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "arrow to vegetables", 
    ["BRAILLE LINE:  'Vegetables ListItem'",
     "     VISIBLE:  'Vegetables ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Vegetables list item expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "collapse vegetables", 
    ["BRAILLE LINE:  'Vegetables ListItem'",
     "     VISIBLE:  'Vegetables ListItem', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

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
