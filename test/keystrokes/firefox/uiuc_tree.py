#!/usr/bin/python

"""Test of UIUC tree presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "application/xhtml+xml: Tree Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/tree/xhtml.php?title=Tree%20Example%201&ginc=includes/tree1a.inc&gcss=css/tree1a.css&gjs=../js/globals.js,../js/enable_app.js,js/tree1a.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("application/xhtml+xml: Tree Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the tree.  The following is presented.
#
# BRAILLE LINE:  'Fruits expanded ListItem LEVEL 1'
#      VISIBLE:  'Fruits expanded ListItem LEVEL 1', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Fruits expanded list item level 1'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Fruits", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Fruits expanded ListItem LEVEL 1'
#      VISIBLE:  'Fruits expanded ListItem LEVEL 1', cursor=1
# SPEECH OUTPUT: 'Fruits'
# SPEECH OUTPUT: 'list item'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Navigate the tree using the arrows.  
#
# BRAILLE LINE:  'Oranges ListItem LEVEL 2'
#      VISIBLE:  'Oranges ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Oranges list item level 2'
# SPEECH OUTPUT: 'tree level 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Oranges", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Pineapples ListItem LEVEL 2'
#      VISIBLE:  'Pineapples ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Pineapples list item level 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Pineapples", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Apples collapsed ListItem LEVEL 2'
#      VISIBLE:  'Apples collapsed ListItem LEVEL ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Apples collapsed list item level 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Apples", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Apples expanded ListItem LEVEL 2'
#      VISIBLE:  'Apples expanded ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: 'expanded'
#
sequence.append(KeyComboAction("Right"))

# BRAILLE LINE:  'Macintosh ListItem LEVEL 3'
#      VISIBLE:  'Macintosh ListItem LEVEL 3', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Macintosh list item level 3'
# SPEECH OUTPUT: 'tree level 3'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Macintosh", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Granny Smith collapsed ListItem LEVEL 3'
#      VISIBLE:  'Granny Smith collapsed ListItem ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Granny Smith collapsed list item level 3'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Granny Smith", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Granny Smith expanded ListItem LEVEL 3'
#      VISIBLE:  'Granny Smith expanded ListItem L', cursor=1
# SPEECH OUTPUT: 'expanded'
#
sequence.append(KeyComboAction("Right"))

# BRAILLE LINE:  'Washington State ListItem LEVEL 4'
#      VISIBLE:  'Washington State ListItem LEVEL ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Washington State list item level 4'
# SPEECH OUTPUT: 'tree level 4'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Washington State", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Michigan ListItem LEVEL 4'
#      VISIBLE:  'Michigan ListItem LEVEL 4', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Michigan list item level 4'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Michigan", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'New York ListItem LEVEL 4'
#      VISIBLE:  'New York ListItem LEVEL 4', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'New York list item level 4'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("New York", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Fuji ListItem LEVEL 3'
#      VISIBLE:  'Fuji ListItem LEVEL 3', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Fuji list item level 3'
# SPEECH OUTPUT: 'tree level 3'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Fuji", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Bananas ListItem LEVEL 2'
#      VISIBLE:  'Bananas ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Bananas list item level 2'
# SPEECH OUTPUT: 'tree level 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Bananas", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Pears ListItem LEVEL 2'
#      VISIBLE:  'Pears ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Pears list item level 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Pears", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Vegetables expanded ListItem LEVEL 1'
#      VISIBLE:  'Vegetables expanded ListItem LEV', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Vegetables expanded list item level 1'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Vegetables", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Vegetables collapsed ListItem LEVEL 1'
#      VISIBLE:  'Vegetables collapsed ListItem LE', cursor=1
#SPEECH OUTPUT: 'collapsed'
#
sequence.append(KeyComboAction("Left"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
