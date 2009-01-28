# -*- coding: utf-8 -*-
#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "form/test_Button.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dojo Button Widget Test", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to <button>  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("<button>", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the <button> button", 
    ["BRAILLE LINE:  '<button> <input type='button'> Button       Create    $l Edit!    $l Color   Save     '",
     "     VISIBLE:  '<button> <input type='button'> B', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '<button> button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on <button>", 
    ["BRAILLE LINE:  '<button> <input type='button'> Button       Create    $l Edit!    $l Color   Save     '",
     "     VISIBLE:  '<button> <input type='button'> B', cursor=1",
     "SPEECH OUTPUT: '<button>'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Tab to <input type='button'>  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("<input type='button'>", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to <input type='button'>",
    ["BRAILLE LINE:  '<button> <input type='button'> Button       Create    $l Edit!    $l Color   Save     '",
     "     VISIBLE:  '<input type='button'> Button    ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '<input type='button'> button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on <input type='button'>", 
    ["BRAILLE LINE:  '<button> <input type='button'> Button       Create    $l Edit!    $l Color   Save     '",
     "     VISIBLE:  '<input type='button'> Button    ', cursor=1",
     "SPEECH OUTPUT: '<input type='button'>'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Tab to "Create"  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Create", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Tab to Create",
    ["BRAILLE LINE:  'Create Button View Button Create Button   Button $l Edit! $l   $l $l Color $l   $lSave Button   Button Disabled Button'",
     "     VISIBLE:  'Create Button View Button Create', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Create button'",
     "SPEECH OUTPUT: 'tooltip on button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on Create", 
    ["BRAILLE LINE:  'Create Button View Button Create Button   Button $l Edit! $l   $l $l Color $l   $lSave Button   Button Disabled Button'",
     "     VISIBLE:  'Create Button View Button Create', cursor=1",
     "SPEECH OUTPUT: 'Create'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: ''"]))

# WDW - Tabbing to the Create button pops up a tooltip.  Should we present
# it automatically?

########################################################################
# Tab to "View", "Create", and then the drop down menu button.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("View", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Create", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Tab to drop down menu on Create", 
    ["BRAILLE LINE:  'Create Button   Button $l Edit! $l   $l $l Color $l   $lSave Button   Button Disabled Button'",
     "     VISIBLE:  '  Button $l Edit! $l   $l $l Col', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '  button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on drop down menu on Create", 
    ["BRAILLE LINE:  'Create Button   Button $l Edit! $l   $l $l Color $l   $lSave Button   Button Disabled Button'",
     "     VISIBLE:  '  Button $l Edit! $l   $l $l Col', cursor=1",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'save options'"]))

########################################################################
# Open the drop down menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Open drop down menu on Create", 
    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345",
     "BRAILLE LINE:  'Create blank'",
     "     VISIBLE:  'Create blank', cursor=1",
     "BRAILLE LINE:  'Menu'",
     "     VISIBLE:  'Menu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Create blank'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'"]))

########################################################################
# Go down a menu item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Create from template", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Down to Create from template", 
    ["BRAILLE LINE:  'Create from template'",
     "     VISIBLE:  'Create from template', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Create from template'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on Create from template", 
    ["BRAILLE LINE:  'Create from template'",
     "     VISIBLE:  'Create from template', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Create from template'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Close the menu and go to the Edit! button
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("  ▼", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Edit!", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Go to Edit!", 
    ["BRAILLE LINE:  ' $l Edit! $l   $l $l Color $l   $lSave Button   Button Disabled Button'",
     "     VISIBLE:  ' $l Edit! $l   $l $l Color $l   ', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Edit! button'"]))

########################################################################
# Open the Edit! menu and navigate through it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Open the Edit! menu", 
    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345",
     "BRAILLE LINE:  'Cut'",
     "     VISIBLE:  'Cut', cursor=1",
     "BRAILLE LINE:  'Menu'",
     "     VISIBLE:  'Menu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Cut'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Copy", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Go to Copy", 
    ["BRAILLE LINE:  'Copy'",
     "     VISIBLE:  'Copy', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Copy'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Paste", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Go to Paste", 
    ["BRAILLE LINE:  'Paste'",
     "     VISIBLE:  'Paste', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Paste'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Goto Submenu", 
    ["BRAILLE LINE:  'Submenu'",
     "     VISIBLE:  'Submenu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Submenu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Open Submenu", 
    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345",
     "BRAILLE LINE:  'Submenu Item One'",
     "     VISIBLE:  'Submenu Item One', cursor=1",
     "BRAILLE LINE:  'Menu'",
     "     VISIBLE:  'Menu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Submenu Item One'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Submenu Item Two", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Down to Submenu Item Two", 
    ["BRAILLE LINE:  'Submenu Item Two'",
     "     VISIBLE:  'Submenu Item Two', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Submenu Item Two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Deeper Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Down to Deeper Submenu", 
    ["BRAILLE LINE:  'Deeper Submenu'",
     "     VISIBLE:  'Deeper Submenu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Deeper Submenu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Right to open Deeper Submenu", 
    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345",
     "BRAILLE LINE:  'Sub-sub-menu Item One'",
     "     VISIBLE:  'Sub-sub-menu Item One', cursor=1",
     "BRAILLE LINE:  'Menu'",
     "     VISIBLE:  'Menu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Sub-sub-menu Item One'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Sub-sub-menu Item Two", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Down to Sub-sub-menu Item Two", 
    ["BRAILLE LINE:  'Sub-sub-menu Item Two'",
     "     VISIBLE:  'Sub-sub-menu Item Two', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Sub-sub-menu Item Two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Deeper Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Close the Deeper Submenu", 
    ["BRAILLE LINE:  'Menu'",
     "     VISIBLE:  'Menu', cursor=1",
     "BRAILLE LINE:  'Deeper Submenu'",
     "     VISIBLE:  'Deeper Submenu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Deeper Submenu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Close the Submenu", 
    ["BRAILLE LINE:  'Menu Menu'",
     "     VISIBLE:  'Menu Menu', cursor=6",
     "BRAILLE LINE:  'Submenu'",
     "     VISIBLE:  'Submenu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Submenu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Edit!", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Close the Edit! menu", 
    ["BRAILLE LINE:  'tooltip on buttonMenu Menu Menu Menu'",
     "     VISIBLE:  'Menu', cursor=1",
     "BRAILLE LINE:  ' $l Edit! $l   $l $l Color $l   $lSave Button   Button Disabled Button'",
     "     VISIBLE:  ' $l Edit! $l   $l $l Color $l   ', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Edit! button'"]))

########################################################################
# Open the Color menu and navigate through it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the Color button", 
    ["BRAILLE LINE:  ' $l Color $l   $lSave Button   Button Disabled Button'",
     "     VISIBLE:  ' $l Color $l   $lSave Button   B', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Color button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("white", acc_role=pyatspi.ROLE_TABLE_CELL))
sequence.append(utils.AssertPresentationAction(
    "Open the Color menu", 
    ["BUG? - speaks 'not selected' apparently due to Down into a table cell",
     "BRAILLE LINE:  'white Image lime Image green Image blue Image'",
     "     VISIBLE:  'white Image lime Image green Ima', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'white'",
     "SPEECH OUTPUT: ' not selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("lime", acc_role=pyatspi.ROLE_TABLE_CELL))
sequence.append(utils.AssertPresentationAction(
    "Go to lime", 
    ["BRAILLE LINE:  'lime Image green Image blue Image'",
     "     VISIBLE:  'lime Image green Image blue Imag', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'lime'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("green", acc_role=pyatspi.ROLE_TABLE_CELL))
sequence.append(utils.AssertPresentationAction(
    "Go to green", 
    ["BRAILLE LINE:  'green Image blue Image'",
     "     VISIBLE:  'green Image blue Image', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'green'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("blue", acc_role=pyatspi.ROLE_TABLE_CELL))
sequence.append(utils.AssertPresentationAction(
    "Go to blue", 
    ["BRAILLE LINE:  'blue Image'",
     "     VISIBLE:  'blue Image', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'blue'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("navy", acc_role=pyatspi.ROLE_TABLE_CELL))
sequence.append(utils.AssertPresentationAction(
    "Go to navy", 
    ["BUG? - speaks 'not selected' apparently due to Down into a table cell",
     "BRAILLE LINE:  'navy Image'",
     "     VISIBLE:  'navy Image', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'navy'",
     "SPEECH OUTPUT: ' not selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("fuchsia", acc_role=pyatspi.ROLE_TABLE_CELL))
sequence.append(utils.AssertPresentationAction(
    "Goto fuchsia", 
    ["BUG? - speaks fuchsia twice when we left arrow to it due to focus and caret-moved",
     "BRAILLE LINE:  'fuchsia Image navy Image'",
     "     VISIBLE:  'fuchsia Image navy Image', cursor=1",
     "BRAILLE LINE:  'fuchsia Image'",
     "     VISIBLE:  'fuchsia Image', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'fuchsia'",
     "SPEECH OUTPUT: 'fuchsia'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("yellow", acc_role=pyatspi.ROLE_TABLE_CELL))
sequence.append(utils.AssertPresentationAction(
    "Goto yellow", 
    ["BUG? - speaks yellow twice when we left arrow to it due to focus and caret-moved",
     "BRAILLE LINE:  'yellow Image fuchsia Image navy Image'",
     "     VISIBLE:  'yellow Image fuchsia Image navy ', cursor=1",
     "BRAILLE LINE:  'yellow Image'",
     "     VISIBLE:  'yellow Image', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'yellow'",
     "SPEECH OUTPUT: 'yellow'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Close the Color menu", 
    ["BRAILLE LINE:  '<button> <input type='button'> Button       Create    $l Edit!    $l Color   Save     '",
     "     VISIBLE:  ' $l Color   Save     ', cursor=1",
     "SPEECH OUTPUT: '<button> button <input type='button'> button Create button   button Edit!   Color   Save button   button'"]))

########################################################################
# Go to the unlabelled buttons
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Rich Text Test!", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the first unlabelled button ('+')", 
    ["BRAILLE LINE:  'Rich Text Test! Button $l   $lSave Button   Button'",
     "     VISIBLE:  'Rich Text Test! Button $l   $lSa', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Rich Text Test! button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the second unlabelled button ('Color')", 
    ["BRAILLE LINE:  ' $l   $lSave Button   Button'",
     "     VISIBLE:  ' $l   $lSave Button   Button', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Color button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the third unlabelled button ('Save')", 
    ["BRAILLE LINE:  ' $l   $lSave Button   Button'",
     "     VISIBLE:  ' $l   $lSave Button   Button', cursor=9",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Save button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("  ▼", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the down arrow button", 
    ["BRAILLE LINE:  ' $l   $lSave Button   Button'",
     "     VISIBLE:  ' $l   $lSave Button   Button', cursor=21",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '  button'"]))

########################################################################
# Tab to the 1st "Toggle me" toggle button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Toggle me", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the 'Toggle me' toggle button", 
    ["BRAILLE LINE:  '&=y Toggle me ToggleButton Toggle me Button'",
     "     VISIBLE:  '&=y Toggle me ToggleButton Toggl', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Toggle me toggle button pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:state-changed:pressed",
                           None,
                           None,
                           pyatspi.ROLE_TOGGLE_BUTTON,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Change the 'Toggle me' toggle button", 
    ["BRAILLE LINE:  '& y Toggle me ToggleButton Toggle me Button'",
     "     VISIBLE:  '& y Toggle me ToggleButton Toggl', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

# Skip this toggle button - it isn't a toggle button.
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Toggle me", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Go through the rest of the buttons.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("big", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the big button", 
    ["BRAILLE LINE:  'big Button small Button long Button'",
     "     VISIBLE:  'big Button small Button long But', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'big button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("small", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the small button", 
    ["BRAILLE LINE:  'small Button'",
     "     VISIBLE:  'small Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'small button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("long", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the long button", 
    ["BRAILLE LINE:  'long Button'",
     "     VISIBLE:  'long Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'long button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("tall", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the tall button", 
    ["BRAILLE LINE:  'tall Button'",
     "     VISIBLE:  'tall Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'tall button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("short", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the short button", 
    ["BRAILLE LINE:  'short Button'",
     "     VISIBLE:  'short Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'short button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("bit longer", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the bit longer button", 
    ["BRAILLE LINE:  'bit longer Button'",
     "     VISIBLE:  'bit longer Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'bit longer button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("ridiculously long", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the ridiculously long button", 
    ["BRAILLE LINE:  'ridiculously long Button'",
     "     VISIBLE:  'ridiculously long Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'ridiculously long button'"]))

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
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
