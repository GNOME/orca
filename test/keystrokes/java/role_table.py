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
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(TypeAction(" "))

##########################################################################
# Tab all the way down to the table.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Table Demo", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Reordering allowed", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Row selection", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Horiz. Lines", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Column selection", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Vert. Lines", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Inter-cell spacing", acc_role=pyatspi.ROLE_SLIDER))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Row height", acc_role=pyatspi.ROLE_SLIDER))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Multiple ranges", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Subsequent columns", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Fit Width", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Print", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TABLE))

##########################################################################
# Tab through the cells.
#

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "Mike" cell:
# 
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "Albers" cell:
# 
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

########################################################################
# [[[BUG 483217: Where am i in JTable cells gives no info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'table'
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# TODO: Is there a keboard way to edit a combo box in a cell?
# Expected output when focus is on "Green" cell:
# 
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "Bazil" cell:
# 
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "44" cell:
# 
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on picture cell:
# 
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on picture cell:
# 
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "3" cell:
# 
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "Curse of the Demon" cell:
# 
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "Blue" cell:
# 
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# [[[BUG 483214: No output when navigating JTable with cursor]]]
# Expected output when focus is on "Andrews" cell:
# 
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# TODO: Also, we get different behavior from Swing when we edit the cell by pressing space as opposed to double clicking with the pointer, in the former the caret is not shown, and pressing return puts us in the cell below it. In the latter the caret is visible, and after pressing return focus stays on the edited cell.
# Edit a cell.
#
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(TypeAction("Andy"))

##########################################################################
# TODO: Pressing return should not put us in the cell below, see todo above.
# Expected output when focus is on cell:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Beck Label'
#      VISIBLE:  'Beck Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Beck label selected'
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Expected output when focus is on cell:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Brian Label'
#      VISIBLE:  'Brian Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Brian label selected'
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Expected output when focus is on cell:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Mark Label'
#      VISIBLE:  'Mark Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mark label selected'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Expected output when focus is on cell:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Andy Label'
#      VISIBLE:  'Andy Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Andy label selected'
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Return cell to previuos text.
#
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(TypeAction("ndrews "))

##########################################################################
# TODO: Pressing return should not put us in the cell below, see todo above.
# Expected output when focus is on cell:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Beck Label'
#      VISIBLE:  'Beck Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Beck label selected'
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Expected output when focus is on cell:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Brian Label'
#      VISIBLE:  'Brian Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Brian label selected'
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Select multiple rows.
#

##########################################################################
# Expected output when row is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Mark Label'
#      VISIBLE:  'Mark Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mark label selected'
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Expected output when row is selected:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo ScrollPane Viewport Table Mike Label'
#      VISIBLE:  'Mike Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mike label selected'
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

########################################################################
# [[[BUG 483217: Where am i in JTable cells gives no info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Mike'
# SPEECH OUTPUT: 'label'
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# Unselect rows. First select only current row, then unselect it.

sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

sequence.append(KeyComboAction("<Control>Space"))


##########################################################################
# Leave table.

sequence.append(KeyComboAction("<Control>Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

# Toggle the top left button, to return to normal state.
sequence.append(TypeAction           (" "))

sequence.append(PauseAction(3000))

sequence.start()
