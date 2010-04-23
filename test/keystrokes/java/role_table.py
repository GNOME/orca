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
# Expected output when focus is on "Mike" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "1. Control Right Arrow into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))

##########################################################################
# Expected output when focus is on "Albers" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "2. Control Right Arrow into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
########################################################################
# [[[BUG 483217: Where am i in JTable cells gives no info]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'table'
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["KNOWN ISSUE - Because of the cell problem, we think the locusOfFocus is the Table",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table'",
     "     VISIBLE:  'Table', cursor=1",
     "SPEECH OUTPUT: 'table'"]))
    
##########################################################################
# TODO: Is there a keboard way to edit a combo box in a cell?
# Expected output when focus is on "Green" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "4 Control Right Arrow into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Expected output when focus is on "Bazil" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "5. Control Right Arrow into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Expected output when focus is on "44" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "6. Control Right Arrow into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Expected output when focus is on picture cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "7. Control Right Arrow into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))

##########################################################################
# Expected output when focus is on picture cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "8. Control Down Arrow into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Expected output when focus is on "3" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "9. Control Left into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Expected output when focus is on "Curse of the Demon" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "10. Control Left into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Expected output when focus is on "Blue" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "11. Control Left into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Expected output when focus is on "Andrews" cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:selection-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "12. Control Left into the cell",
    ["BUG? - No output when navigating JTable with cursor. See bug 483214."]))
    
##########################################################################
# Press Space Bar on the current cell
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "13. Space Bar on the cell",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table Last Name ColumnHeader Andrews'",
     "     VISIBLE:  'Andrews', cursor=1",
     "SPEECH OUTPUT: 'Last Name column header Andrews'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "14. Remove the text in the cell.",
    ["BUG? - We aren't told what text is being removed. I believe this is due to the lack of any_data."]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("Andy"))
sequence.append(utils.AssertPresentationAction(
    "15. Type 'Andy' into the cell",
    ["BUG? - We're not presenting anything here."]))

##########################################################################
# Expected output when focus is on cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "16. Press Return",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table Last Name ColumnHeader Beck'",
     "     VISIBLE:  'Beck', cursor=1",
     "SPEECH OUTPUT: 'Last Name column header Beck'"]))

##########################################################################
# Expected output when focus is on cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "17. Press Left Arrow",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table First Name ColumnHeader Brian'",
     "     VISIBLE:  'Brian', cursor=1",
     "SPEECH OUTPUT: 'First Name column header Brian'"]))
    
##########################################################################
# Expected output when focus is on cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "18. Press Up Arrow",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table First Name ColumnHeader Mark'",
     "     VISIBLE:  'Mark', cursor=1",
     "SPEECH OUTPUT: 'First Name column header Mark'"]))
    
##########################################################################
# Expected output when focus is on cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "19. Press Right Arrow",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table Last Name ColumnHeader Andy'",
     "     VISIBLE:  'Andy', cursor=1",
     "SPEECH OUTPUT: 'Last Name column header Andy'"]))
    
##########################################################################
# Return cell to previous text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "20. Press Space Bar",
    ["BUG? - We're not presenting anything here."]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(TypeAction("ndrews "))
sequence.append(utils.AssertPresentationAction(
    "21. BackSpace over the newly-added text and type 'ndrews'",
    ["BUG? - We're not presenting anything here."]))
    
##########################################################################
# Expected output when focus is on cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "22. Press Return",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table Last Name ColumnHeader Beck'",
     "     VISIBLE:  'Beck', cursor=1",
     "SPEECH OUTPUT: 'Last Name column header Beck'"]))
    
##########################################################################
# Expected output when focus is on cell:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "23. Press Left Arrow",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table First Name ColumnHeader Brian'",
     "     VISIBLE:  'Brian', cursor=1",
     "SPEECH OUTPUT: 'First Name column header Brian'"]))
    
##########################################################################
# Expected output when row is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "24. Shift Up Arrow to select the row",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table First Name ColumnHeader Mark'",
     "     VISIBLE:  'Mark', cursor=1",
     "SPEECH OUTPUT: 'First Name column header Mark'"]))
    
##########################################################################
# Expected output when row is selected:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(utils.AssertPresentationAction(
    "25. Shift Up Arrow to select the row",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table First Name ColumnHeader Mike'",
     "     VISIBLE:  'Mike', cursor=1",
     "SPEECH OUTPUT: 'Mike'"]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "26. Basic Where Am I",
    ["BUG? - Not much detail. See bug 483217.",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Table Demo TabList Table Demo Page ScrollPane Viewport Table First Name ColumnHeader Mike'",
     "     VISIBLE:  'Mike', cursor=1",
     "SPEECH OUTPUT: 'Mike'"]))
    
##########################################################################
# Unselect rows. First select only current row, then unselect it.

sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:active-descendant-changed", None, None,
                           pyatspi.ROLE_TABLE, 5000))

##########################################################################
# Leave table.

sequence.append(KeyComboAction("<Control>Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

# Toggle the top left button, to return to normal state.
sequence.append(TypeAction(" "))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
