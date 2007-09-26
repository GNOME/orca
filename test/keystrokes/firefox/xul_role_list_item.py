#!/usr/bin/python

"""Test of list item output using Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "Edit" menu and Up Arrow to Preferences, then press Return.
#
sequence.append(KeyComboAction("<Alt>e"))
sequence.append(WaitForFocus("Undo", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Preferences", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))

########################################################################
# We wait for the Preferences dialog to appear.  Focus should be on the
# Main list item.  [[[Bug: Orca reads the entire list.  Should it??  
# We also seem to be missing a focus: event for the "Main" list item.
# Lack of proper focus events in dialogs is a known issue that Aaron is 
# working on.]]]
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog'
#      VISIBLE:  'Minefield Preferences Dialog', cursor=1
# SPEECH OUTPUT: 'Minefield Preferences Main Tabs Content Applications Privacy Security Advanced'
#
sequence.append(WaitForWindowActivate("Minefield Preferences",None))

########################################################################
# Press Right Arrow to move forward to the "Tabs" list item.
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog List Tabs ListItem'
#      VISIBLE:  'Tabs ListItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tabs'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tabs", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Right Arrow to move forward to the "Content" list item.
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog List Content ListItem'
#     VISIBLE:  'Content ListItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Content'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Content", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Right Arrow to move forward to the "Applications" list item.
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog List Applications ListItem'
#      VISIBLE:  'Applications ListItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Applications'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Applications", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Left Arrow to move back to the "Content" list item.
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog List Content ListItem'
#     VISIBLE:  'Content ListItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Content'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Content", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Left Arrow to move back to the "Tabs" list item.
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog List Tabs ListItem'
#      VISIBLE:  'Tabs ListItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tabs'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Tabs", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Left Arrow to move back to the "Main" list item.
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog List Main ListItem'
#      VISIBLE:  'Main ListItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Main'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Main", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  [[[Bug: The current where am I 
# doesn't handle list items per se but treats them as generic.  We 
# probably want to treat them more like items in a tree?]]]
# 
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog List Main ListItem'
#      VISIBLE:  'Main ListItem', cursor=1
# SPEECH OUTPUT: 'Main'
# SPEECH OUTPUT: 'list item'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
