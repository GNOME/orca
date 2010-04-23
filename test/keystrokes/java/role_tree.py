#!/usr/bin/python

"""Test of push buttons in Java's SwingSet2."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

# Wait for entire window to get populated.
sequence.append(PauseAction(5000))

##########################################################################
# Tab over to the button demo, and activate it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(TypeAction(" "))

##########################################################################
# Tab all the way down to the tree.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Tree Demo", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TREE))

##########################################################################
# Expected output when node is selected:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree Music expanded TREE LEVEL 1'",
     "     VISIBLE:  'Music expanded TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: 'Music expanded 3 items tree level 1'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Classical collapsed TREE LEVEL 2'",
     "     VISIBLE:  'Classical collapsed TREE LEVEL 2', cursor=1",
     "SPEECH OUTPUT: 'Classical collapsed tree level 2'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Jazz collapsed TREE LEVEL 2'",
     "     VISIBLE:  'Jazz collapsed TREE LEVEL 2', cursor=1",
     "SPEECH OUTPUT: 'Jazz collapsed'"]))
    
##########################################################################
# Expected output when node is expanded:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "4. Right Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Jazz expanded TREE LEVEL 2'",
     "     VISIBLE:  'Jazz expanded TREE LEVEL 2', cursor=1",
     "SPEECH OUTPUT: 'expanded 4 items'"]))
    
##########################################################################
# Expected output when node is selected:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Albert Ayler collapsed TREE LEVEL 3'",
     "     VISIBLE:  'Albert Ayler collapsed TREE LEVE', cursor=1",
     "SPEECH OUTPUT: 'Albert Ayler collapsed tree level 3'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "6. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Chet Baker collapsed TREE LEVEL 3'",
     "     VISIBLE:  'Chet Baker collapsed TREE LEVEL ', cursor=1",
     "SPEECH OUTPUT: 'Chet Baker collapsed'"]))

##########################################################################
# Expected output when node is expanded:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "7. Right Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Chet Baker expanded TREE LEVEL 3'",
     "     VISIBLE:  'Chet Baker expanded TREE LEVEL 3', cursor=1",
     "SPEECH OUTPUT: 'expanded 4 items'"]))
    
##########################################################################
# Expected output when node is expanded:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "8. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Sings and Plays collapsed TREE LEVEL 4'",
     "     VISIBLE:  'Sings and Plays collapsed TREE L', cursor=1",
     "SPEECH OUTPUT: 'Sings and Plays collapsed tree level 4'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application My Funny Valentine collapsed TREE LEVEL 4'",
     "     VISIBLE:  'My Funny Valentine collapsed TRE', cursor=1",
     "SPEECH OUTPUT: 'My Funny Valentine collapsed'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "10. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December collapsed TREE LEVEL 4'",
     "     VISIBLE:  'Grey December collapsed TREE LEV', cursor=1",
     "SPEECH OUTPUT: 'Grey December collapsed'"]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "11. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December collapsed TREE LEVEL 4'",
     "     VISIBLE:  'Grey December collapsed TREE LEV', cursor=1",
     "SPEECH OUTPUT: 'Grey December collapsed tree level 4'"]))
    
##########################################################################
# Expected output when node is expanded:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "12. Right Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December expanded TREE LEVEL 4'",
     "     VISIBLE:  'Grey December expanded TREE LEVE', cursor=1",
     "SPEECH OUTPUT: 'expanded 9 items'"]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "13. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December expanded TREE LEVEL 4'",
     "     VISIBLE:  'Grey December expanded TREE LEVE', cursor=1",
     "SPEECH OUTPUT: 'Grey December expanded 9 items tree level 4'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "14. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December TREE LEVEL 5'",
     "     VISIBLE:  'Grey December TREE LEVEL 5', cursor=1",
     "SPEECH OUTPUT: 'Grey December tree level 5'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "15. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application I Wish I Knew TREE LEVEL 5'",
     "     VISIBLE:  'I Wish I Knew TREE LEVEL 5', cursor=1",
     "SPEECH OUTPUT: 'I Wish I Knew'"]))
    
##########################################################################
# Expected output when node is selected:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "16. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Someone To Watch Over Me TREE LEVEL 5'",
     "     VISIBLE:  'Someone To Watch Over Me TREE LE', cursor=1",
     "SPEECH OUTPUT: 'Someone To Watch Over Me'"]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "17. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application Someone To Watch Over Me TREE LEVEL 5'",
     "     VISIBLE:  'Someone To Watch Over Me TREE LE', cursor=1",
     "SPEECH OUTPUT: 'Someone To Watch Over Me tree level 5'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "18. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application I Wish I Knew TREE LEVEL 5'",
     "     VISIBLE:  'I Wish I Knew TREE LEVEL 5', cursor=1",
     "SPEECH OUTPUT: 'I Wish I Knew'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "19. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December TREE LEVEL 5'",
     "     VISIBLE:  'Grey December TREE LEVEL 5', cursor=1",
     "SPEECH OUTPUT: 'Grey December'"]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "20. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December expanded TREE LEVEL 4'",
     "     VISIBLE:  'Grey December expanded TREE LEVE', cursor=1",
     "SPEECH OUTPUT: 'Grey December expanded 9 items tree level 4'"]))
    
##########################################################################
# Expected output when node is collaped:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "21. Left Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December collapsed TREE LEVEL 4'",
     "     VISIBLE:  'Grey December collapsed TREE LEV', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "22. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application My Funny Valentine collapsed TREE LEVEL 4'",
     "     VISIBLE:  'My Funny Valentine collapsed TRE', cursor=1",
     "SPEECH OUTPUT: 'My Funny Valentine collapsed'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "23. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Sings and Plays collapsed TREE LEVEL 4'",
     "     VISIBLE:  'Sings and Plays collapsed TREE L', cursor=1",
     "SPEECH OUTPUT: 'Sings and Plays collapsed'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "24. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Chet Baker expanded TREE LEVEL 3'",
     "     VISIBLE:  'Chet Baker expanded TREE LEVEL 3', cursor=1",
     "SPEECH OUTPUT: 'Chet Baker expanded 4 items tree level 3'"]))
    
##########################################################################
# Expected output when node is collaped:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "25. Left Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Chet Baker collapsed TREE LEVEL 3'",
     "     VISIBLE:  'Chet Baker collapsed TREE LEVEL ', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "26. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Albert Ayler collapsed TREE LEVEL 3'",
     "     VISIBLE:  'Albert Ayler collapsed TREE LEVE', cursor=1",
     "SPEECH OUTPUT: 'Albert Ayler collapsed'"]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "27. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Jazz expanded TREE LEVEL 2'",
     "     VISIBLE:  'Jazz expanded TREE LEVEL 2', cursor=1",
     "SPEECH OUTPUT: 'Jazz expanded 4 items tree level 2'"]))

##########################################################################
# Expected output when node is collaped:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "28. Left Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Jazz collapsed TREE LEVEL 2'",
     "     VISIBLE:  'Jazz collapsed TREE LEVEL 2', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "29. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Classical collapsed TREE LEVEL 2'",
     "     VISIBLE:  'Classical collapsed TREE LEVEL 2', cursor=1",
     "SPEECH OUTPUT: 'Classical collapsed"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "30. Up Arrow in the tree",
    ["BUG? - Seems a bit chatty",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree Music expanded TREE LEVEL 1'",
     "     VISIBLE:  'Music expanded TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page Music expanded 3 items tree level 1'"]))
    
##########################################################################
# Leave tree
# 
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

sequence.append(KeyComboAction("Tab"))

# Toggle the top left button, to return to normal state.
sequence.append(TypeAction(" "))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
