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
     "SPEECH OUTPUT: 'Music expanded tree level 1'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Classical collapsed'",
     "     VISIBLE:  'Classical collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Classical collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Jazz collapsed'",
     "     VISIBLE:  'Jazz collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Jazz collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is expanded:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "4. Right Arrow in the tree",
    ["BUG? - We're not presenting anything here. Should be told Jazz is expanded."]))
    
##########################################################################
# Expected output when node is selected:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Albert Ayler collapsed'",
     "     VISIBLE:  'Albert Ayler collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Albert Ayler collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "6. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Chet Baker collapsed'",
     "     VISIBLE:  'Chet Baker collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Chet Baker collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))

##########################################################################
# Expected output when node is expanded:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "7. Right Arrow in the tree",
    ["BUG? - We're not presenting anything here. Should be told Chet Baker is expanded."]))
    
##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Sings and Plays Label'
#      VISIBLE:  'Sings and Plays Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label'
# SPEECH OUTPUT: 'Sings and Plays label collapsed'
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "8. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Sings and Plays collapsed'",
     "     VISIBLE:  'Sings and Plays collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Sings and Plays collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application My Funny Valentine collapsed'",
     "     VISIBLE:  'My Funny Valentine collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'My Funny Valentine collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "10. Down Arrow in the tree",
    ["BUG? - Looks like the tree is becoming the locusOfFocus. It shouldn't be.",
     "BRAILLE LINE:  'SwingSet2 Application Grey December collapsed'",
     "     VISIBLE:  'Grey December collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Grey December collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
########################################################################
# [[[BUG 483222: Where am i in JTree nodes gives little info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "11. Basic Where Am I",
    ["BUG? - Little detail - see bug 483222. Also, why is the tree the locusOfFocus?",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'tree'"]))
    
##########################################################################
# Expected output when node is expanded:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "12. Right Arrow in the tree",
    ["BUG? - We're not presenting anything here. Should be told Grey December is expanded."]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "13. Basic Where Am I",
    ["BUG? - Little detail - see bug 483222. Also, why is the tree the locusOfFocus?",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "14. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December'",
     "     VISIBLE:  'Grey December', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Grey December'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "15. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application I Wish I Knew'",
     "     VISIBLE:  'I Wish I Knew', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'I Wish I Knew'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "16. Down Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Someone To Watch Over Me'",
     "     VISIBLE:  'Someone To Watch Over Me', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Someone To Watch Over Me'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
########################################################################
# [[[BUG 483222: Where am i in JTree nodes gives little info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Someone To Watch Over Me'
# SPEECH OUTPUT: 'label'
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "17. Basic Where Am I",
    ["BUG? - Little detail - see bug 483222. Also, why is the tree the locusOfFocus?",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "18. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application I Wish I Knew'",
     "     VISIBLE:  'I Wish I Knew', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'I Wish I Knew'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "19. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December'",
     "     VISIBLE:  'Grey December', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Grey December'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "20. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Grey December expanded'",
     "     VISIBLE:  'Grey December expanded', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Grey December expanded'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is collaped:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "21. Left Arrow in the tree",
    ["BUG? - We're not presenting anything here. Should be told Grey December is collapsed."]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "22. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application My Funny Valentine collapsed'",
     "     VISIBLE:  'My Funny Valentine collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'My Funny Valentine collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "23. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Sings and Plays collapsed'",
     "     VISIBLE:  'Sings and Plays collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Sings and Plays collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "24. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Chet Baker expanded'",
     "     VISIBLE:  'Chet Baker expanded', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Chet Baker expanded'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is collaped:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "25. Left Arrow in the tree",
    ["BUG? - We're not presenting anything here. Should be told Chet Baker is collapsed."]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "26. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Albert Ayler collapsed'",
     "     VISIBLE:  'Albert Ayler collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Albert Ayler collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "27. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Jazz expanded'",
     "     VISIBLE:  'Jazz expanded', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Jazz expanded'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))

##########################################################################
# Expected output when node is collaped:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))
sequence.append(utils.AssertPresentationAction(
    "28. Left Arrow in the tree",
    ["BUG? - We're not presenting anything here. Should be told Jazz is collapsed."]))

##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "29. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application Classical collapsed'",
     "     VISIBLE:  'Classical collapsed', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree'",
     "     VISIBLE:  'Tree', cursor=1",
     "SPEECH OUTPUT: 'Classical collapsed'",
     "SPEECH OUTPUT: 'SwingSet2 frame Tree Demo tab list Tree Demo page tree'"]))
    
##########################################################################
# Expected output when node is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(utils.AssertPresentationAction(
    "30. Up Arrow in the tree",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo Page ScrollPane Viewport Tree Music expanded TREE LEVEL 1'",
     "     VISIBLE:  'Music expanded TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: 'Music expanded tree level 1'"]))
    
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
