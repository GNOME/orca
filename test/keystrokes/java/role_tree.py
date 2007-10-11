#!/usr/bin/python

"""Test of push buttons in Java's SwingSet2.
"""

from macaroon.playback.keypress_mimic import *

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
# Navigate tree.
#

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label'
#      VISIBLE:  'Music Label', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Music label expanded'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Classical Label'
#      VISIBLE:  'Classical Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label'
# SPEECH OUTPUT: 'Classical label collapsed'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label'
#      VISIBLE:  'Jazz Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label'
# SPEECH OUTPUT: 'Jazz label expanded'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is expanded:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label'
#      VISIBLE:  'Jazz Label', cursor=1
# SPEECH OUTPUT: 'expanded'
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Albert Ayler Label'
#      VISIBLE:  'Albert Ayler Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label'
# SPEECH OUTPUT: 'Albert Ayler label collapsed'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label'
#      VISIBLE:  'Chet Baker Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label'
# SPEECH OUTPUT: 'Chet Baker label collapsed'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is expanded:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label'
#      VISIBLE:  'Chet Baker Label', cursor=1
# SPEECH OUTPUT: 'expanded'
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Sings and Plays Label'
#      VISIBLE:  'Sings and Plays Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label'
# SPEECH OUTPUT: 'Sings and Plays label collapsed'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label My Funny Valentine Label'
#      VISIBLE:  'My Funny Valentine Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label'
# SPEECH OUTPUT: 'My Funny Valentine label collapsed'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label'
#      VISIBLE:  'Grey December Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label'
# SPEECH OUTPUT: 'Grey December label collapsed'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

########################################################################
# [[[BUG 483222: Where am i in JTree nodes gives little info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Grey December'
# SPEECH OUTPUT: 'label'
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is expanded:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label'
#      VISIBLE:  'Grey December Label', cursor=1
# SPEECH OUTPUT: 'expanded'
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))

########################################################################
# [[[BUG 483222: Where am i in JTree nodes gives little info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Grey December'
# SPEECH OUTPUT: 'label'
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label Grey December Label'
#      VISIBLE:  'Grey December Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label Grey December label'
# SPEECH OUTPUT: 'Grey December label'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label I Wish I Knew Label'
#      VISIBLE:  'I Wish I Knew Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label Grey December label'
# SPEECH OUTPUT: 'I Wish I Knew label selected'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label Someone To Watch Over Me Label'
#      VISIBLE:  'Someone To Watch Over Me Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label Grey December label'
# SPEECH OUTPUT: 'Someone To Watch Over Me label selected'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

########################################################################
# [[[BUG 483222: Where am i in JTree nodes gives little info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Someone To Watch Over Me'
# SPEECH OUTPUT: 'label'
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label I Wish I Knew Label'
#      VISIBLE:  'I Wish I Knew Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label Grey December label'
# SPEECH OUTPUT: 'I Wish I Knew label selected'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label Grey December Label'
#      VISIBLE:  'Grey December Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label Grey December label'
# SPEECH OUTPUT: 'Grey December label selected'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label'
#      VISIBLE:  'Grey December Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label'
# SPEECH OUTPUT: 'Grey December label expanded'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is collaped:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Grey December Label'
#      VISIBLE:  'Grey December Label', cursor=1
# SPEECH OUTPUT: 'collapsed'
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))


##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label My Funny Valentine Label'
#      VISIBLE:  'My Funny Valentine Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label'
# SPEECH OUTPUT: 'My Funny Valentine label collapsed'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label Sings and Plays Label'
#      VISIBLE:  'Sings and Plays Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label Chet Baker label'
# SPEECH OUTPUT: 'Sings and Plays label collapsed'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label'
#      VISIBLE:  'Chet Baker Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label'
# SPEECH OUTPUT: 'Chet Baker label expanded'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is collaped:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Chet Baker Label'
#      VISIBLE:  'Chet Baker Label', cursor=1
# SPEECH OUTPUT: 'collapsed'
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label Albert Ayler Label'
#      VISIBLE:  'Albert Ayler Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label Jazz label'
# SPEECH OUTPUT: 'Albert Ayler label collapsed'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label'
#      VISIBLE:  'Jazz Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label'
# SPEECH OUTPUT: 'Jazz label expanded'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is collaped:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Jazz Label'
#      VISIBLE:  'Jazz Label', cursor=1
# SPEECH OUTPUT: 'collapsed'
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:state-changed:expanded", None, None,
                           pyatspi.ROLE_LABEL, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label Classical Label'
#      VISIBLE:  'Classical Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page Music label'
# SPEECH OUTPUT: 'Classical label collapsed'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))

##########################################################################
# [[[BUG 483219: JTree nodes don't show expanded or collapsed in braille]]]
# [[[BUG 483221: When traversing jtree nodes the entire context is announced again and again]]]
# Expected output when node is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Tree Demo TabList Tree Demo ScrollPane Viewport Tree Music Label'
#      VISIBLE:  'Music Label', cursor=1
# SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Tree Demo tab list Tree Demo page'
# SPEECH OUTPUT: 'Music label expanded'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TREE, 5000))
sequence.append(KeyComboAction("Tab"))

##########################################################################
# Leave tree
# 
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

# Toggle the top left button, to return to normal state.
sequence.append(TypeAction           (" "))

sequence.append(PauseAction(3000))

sequence.start()
