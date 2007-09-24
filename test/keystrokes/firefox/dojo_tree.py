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
# Tab to the first tree.  The following will be presented.
#
# BRAILLE LINE:  'Africa ListItem LEVEL 1'
#      VISIBLE:  'Africa ListItem LEVEL 1', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Africa list item level 1'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Africa", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille.  Note:  focus is never on the tree itself.
#
# BRAILLE LINE:  'Africa ListItem LEVEL 1'
#      VISIBLE:  'Africa ListItem LEVEL 1', cursor=1
# SPEECH OUTPUT: 'Africa'
# SPEECH OUTPUT: 'list item'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
########################################################################
# Use arrows to expand/collapse/navigate tree.  The following will be presented after
# each step.
#
# BRAILLE LINE:  'Africa expanded ListItem LEVEL 1'
#      VISIBLE:  'Africa expanded ListItem LEVEL 1', cursor=1
# SPEECH OUTPUT: 'expanded'
sequence.append(KeyComboAction("Right"))

# BRAILLE LINE:  'Egypt ListItem LEVEL 2'
#      VISIBLE:  'Egypt ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Egypt list item level 2'
# SPEECH OUTPUT: 'tree level 2'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Egypt", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Kenya ListItem LEVEL 2'
#      VISIBLE:  'Kenya ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Kenya list item level 2'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Kenya", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Kenya expanded ListItem LEVEL 2'
#      VISIBLE:  'Kenya expanded ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: 'expanded'
sequence.append(KeyComboAction("Right"))

# BRAILLE LINE:  'Kenya collapsed ListItem LEVEL 2'
#      VISIBLE:  'Kenya collapsed ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: 'collapsed'
sequence.append(KeyComboAction("Left"))

# BRAILLE LINE:  'Sudan ListItem LEVEL 2'
#      VISIBLE:  'Sudan ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Sudan list item level 2'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Sudan", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Asia ListItem LEVEL 1'
#      VISIBLE:  'Asia ListItem LEVEL 1', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Asia list item level 1'
# SPEECH OUTPUT: 'tree level 1'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Asia", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Asia expanded ListItem LEVEL 1'
#      VISIBLE:  'Asia expanded ListItem LEVEL 1', cursor=1
# SPEECH OUTPUT: 'expanded'
sequence.append(KeyComboAction("Right"))

# BRAILLE LINE:  'China ListItem LEVEL 2'
#      VISIBLE:  'China ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'China list item level 2'
# SPEECH OUTPUT: 'tree level 2'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("China", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'India ListItem LEVEL 2'
#      VISIBLE:  'India ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'India list item level 2'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("India", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Russia ListItem LEVEL 2'
#      VISIBLE:  'Russia ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Russia list item level 2'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Russia", acc_role=pyatspi.ROLE_LIST_ITEM))

# BRAILLE LINE:  'Mongolia ListItem LEVEL 2'
#      VISIBLE:  'Mongolia ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mongolia list item level 2'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Mongolia", acc_role=pyatspi.ROLE_LIST_ITEM))
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

sequence.start()
