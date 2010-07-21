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
sequence.append(utils.AssertPresentationAction(
    "Tab to the <button> button", 
    ["BRAILLE LINE:  '<button> <input type='button'> Create  View  Createsave options Menu'",
     "     VISIBLE:  '<button> <input type='button'> C', cursor=1",
     "SPEECH OUTPUT: '<button> button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on <button>", 
    ["BRAILLE LINE:  '<button> <input type='button'> Create  View  Createsave options Menu'",
     "     VISIBLE:  '<button> <input type='button'> C', cursor=1",
     "SPEECH OUTPUT: '<button> button'"]))

########################################################################
# Tab to <input type='button'>  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to <input type='button'>",
    ["BUG? - Missing a space between 'Create' and 'save'",
     "BRAILLE LINE:  '<button> <input type='button'> Create  View  Createsave options Menu'",
     "     VISIBLE:  '<input type='button'> Create  Vi', cursor=1",
     "SPEECH OUTPUT: '<input type='button'> button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on <input type='button'>", 
    ["BRAILLE LINE:  '<button> <input type='button'> Create  View  Createsave options Menu'",
     "     VISIBLE:  '<input type='button'> Create  Vi', cursor=1",
     "SPEECH OUTPUT: '<input type='button'> button'"]))

########################################################################
# Tab to "Create"  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Tab to Create",
    ["BRAILLE LINE:  '<button> <input type='button'> Create  View  Createsave options Menu'",
     "     VISIBLE:  'Create  View  Createsave options', cursor=1",
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
    ["BRAILLE LINE:  '<button> <input type='button'> Create  View  Createsave options Menu'",
     "     VISIBLE:  'Create  View  Createsave options', cursor=1",
     "SPEECH OUTPUT: 'Create button'"]))

# WDW - Tabbing to the Create button pops up a tooltip.  Should we present
# it automatically?

########################################################################
# Tab to "View", "Create", and then the drop down menu button.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to drop down menu on Create", 
    ["BRAILLE LINE:  '<button> Button <input type='button'> Button $lsave options Menu'",
     "     VISIBLE:  'save options Menu', cursor=1",
     "SPEECH OUTPUT: 'save options menu'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I on drop down menu on Create", 
    ["BRAILLE LINE:  '<button> Button <input type='button'> Button $lsave options Menu'",
     "     VISIBLE:  'save options Menu', cursor=1",
     "SPEECH OUTPUT: 'save options menu'"]))

########################################################################
# Open the drop down menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Open drop down menu on Create", 
    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345. In addition, the demo is broken at the moment."]))
#     "BRAILLE LINE:  'Create blank'",
#     "     VISIBLE:  'Create blank', cursor=1",
#     "BRAILLE LINE:  'Menu'",
#     "     VISIBLE:  'Menu', cursor=1",
#     "SPEECH OUTPUT: 'Create blank'",
#     "SPEECH OUTPUT: 'menu'"]))

########################################################################
# Go down a menu item.
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Create from template", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Down to Create from template",
#    ["KNOWN ISSUE -- demo is broken at the moment."]))
#     "BRAILLE LINE:  'Create from template'",
#     "     VISIBLE:  'Create from template', cursor=1",
#     "SPEECH OUTPUT: 'Create from template'"]))

########################################################################
# Close the menu and go to the Edit! button
#
#sequence.append(KeyComboAction("Escape"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Go to Edit!", 
    ["BRAILLE LINE:  'Edit! Color Savesave options Menu Disabled '",
     "     VISIBLE:  'Edit! Color Savesave options Men', cursor=1",
     "SPEECH OUTPUT: 'Edit! menu'"]))

########################################################################
# Open the Edit! menu and navigate through it.
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))
#sequence.append(utils.AssertPresentationAction(
#    "Open the Edit! menu", 
#    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345. In addition, the demo is broken at the moment."]))
#     "BRAILLE LINE:  'Cut'",
#     "     VISIBLE:  'Cut', cursor=1",
#     "BRAILLE LINE:  'Menu'",
#     "     VISIBLE:  'Menu', cursor=1",
#     "SPEECH OUTPUT: 'Cut'",
#     "SPEECH OUTPUT: 'menu'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Copy", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Go to Copy", 
#    ["BRAILLE LINE:  'Copy'",
#     "     VISIBLE:  'Copy', cursor=1",
#     "SPEECH OUTPUT: 'Copy'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Paste", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Go to Paste", 
#    ["BRAILLE LINE:  'Paste'",
#     "     VISIBLE:  'Paste', cursor=1",
#     "SPEECH OUTPUT: 'Paste'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Goto Submenu", 
#    ["BRAILLE LINE:  'Submenu'",
#     "     VISIBLE:  'Submenu', cursor=1",
#     "SPEECH OUTPUT: 'Submenu'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Right"))
#sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))
#sequence.append(utils.AssertPresentationAction(
#    "Open Submenu", 
#    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345",
#     "BRAILLE LINE:  'Menu'",
#     "     VISIBLE:  'Menu', cursor=1",
#     "BRAILLE LINE:  'Submenu Item One'",
#     "     VISIBLE:  'Submenu Item One', cursor=1",
#     "SPEECH OUTPUT: 'menu'",
#     "SPEECH OUTPUT: 'Submenu Item One'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Submenu Item Two", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Down to Submenu Item Two", 
#    ["BRAILLE LINE:  'Submenu Item Two'",
#     "     VISIBLE:  'Submenu Item Two', cursor=1",
#     "SPEECH OUTPUT: 'Submenu Item Two'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Deeper Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Down to Deeper Submenu", 
#    ["BRAILLE LINE:  'Deeper Submenu'",
#     "     VISIBLE:  'Deeper Submenu', cursor=1",
#     "SPEECH OUTPUT: 'Deeper Submenu'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Right"))
#sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_MENU))
#sequence.append(utils.AssertPresentationAction(
#    "Right to open Deeper Submenu", 
#    ["KNOWN ISSUE -- http://bugzilla.gnome.org/show_bug.cgi?id=569345",
#     "BRAILLE LINE:  'Menu'",
#     "     VISIBLE:  'Menu', cursor=1",
#     "BRAILLE LINE:  'Sub-sub-menu Item One'",
#     "     VISIBLE:  'Sub-sub-menu Item One', cursor=1",
#     "SPEECH OUTPUT: 'menu'",
#     "SPEECH OUTPUT: 'Sub-sub-menu Item One'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Sub-sub-menu Item Two", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Down to Sub-sub-menu Item Two", 
#    ["BRAILLE LINE:  'Sub-sub-menu Item Two'",
#     "     VISIBLE:  'Sub-sub-menu Item Two', cursor=1",
#     "SPEECH OUTPUT: 'Sub-sub-menu Item Two'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Escape"))
#sequence.append(WaitForFocus("Deeper Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Close the Deeper Submenu", 
#    ["BRAILLE LINE:  'Menu'",
#     "     VISIBLE:  'Menu', cursor=1",
#     "BRAILLE LINE:  'Deeper Submenu'",
#     "     VISIBLE:  'Deeper Submenu', cursor=1",
#     "SPEECH OUTPUT: 'menu'",
#     "SPEECH OUTPUT: 'Deeper Submenu'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Escape"))
#sequence.append(WaitForFocus("Submenu", acc_role=pyatspi.ROLE_MENU_ITEM))
#sequence.append(utils.AssertPresentationAction(
#    "Close the Submenu", 
#    ["BRAILLE LINE:  'Menu Menu'",
#     "     VISIBLE:  'Menu Menu', cursor=6",
#     "BRAILLE LINE:  'Submenu'",
#     "     VISIBLE:  'Submenu', cursor=1",
#     "SPEECH OUTPUT: 'menu'",
#     "SPEECH OUTPUT: 'Submenu'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Escape"))
#sequence.append(WaitForFocus("Edit!", acc_role=pyatspi.ROLE_PUSH_BUTTON))
#sequence.append(utils.AssertPresentationAction(
#    "Close the Edit! menu", 
#    ["BUG? - Why does it say Edit! twice?",
#     "BRAILLE LINE:  'tooltip on buttonMenu Menu Menu Menu'",
#     "     VISIBLE:  'Menu', cursor=1",
#     "BRAILLE LINE:  'Edit! Edit! Menu'",
#     "     VISIBLE:  'Edit! Edit! Menu', cursor=1",
#     "SPEECH OUTPUT: 'menu'",
#     "SPEECH OUTPUT: 'Edit! menu'"]))

########################################################################
# Open the Color menu and navigate through it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the Color button", 
    ["BRAILLE LINE:  'Color Savesave options Menu Disabled '",
     "     VISIBLE:  'Color Savesave options Menu Disa', cursor=1",
     "SPEECH OUTPUT: 'Color menu'"]))

#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("white", acc_role=pyatspi.ROLE_TABLE_CELL))
#sequence.append(utils.AssertPresentationAction(
#    "Open the Color menu", 
#    ["BUG? - speaks 'not selected' apparently due to Down into a table cell",
#     "BRAILLE LINE:  'white Image lime Image green Image blue Image'",
#     "     VISIBLE:  'white Image lime Image green Ima', cursor=1",
#     "SPEECH OUTPUT: 'white not selected'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Right"))
#sequence.append(WaitForFocus("lime", acc_role=pyatspi.ROLE_TABLE_CELL))
#sequence.append(utils.AssertPresentationAction(
#    "Go to lime", 
#    ["BRAILLE LINE:  'white Image lime Image green Image blue Image'",
#     "     VISIBLE:  'lime Image green Image blue Imag', cursor=1",
#     "SPEECH OUTPUT: 'lime'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Right"))
#sequence.append(WaitForFocus("green", acc_role=pyatspi.ROLE_TABLE_CELL))
#sequence.append(utils.AssertPresentationAction(
#    "Go to green", 
#    ["BRAILLE LINE:  'white Image lime Image green Image blue Image'",
#     "     VISIBLE:  'green Image blue Image', cursor=1",
#     "SPEECH OUTPUT: 'green'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Right"))
#sequence.append(WaitForFocus("blue", acc_role=pyatspi.ROLE_TABLE_CELL))
#sequence.append(utils.AssertPresentationAction(
#    "Go to blue", 
#    ["BRAILLE LINE:  'white Image lime Image green Image blue Image'",
#     "     VISIBLE:  'blue Image', cursor=1",
#     "SPEECH OUTPUT: 'blue'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("navy", acc_role=pyatspi.ROLE_TABLE_CELL))
#sequence.append(utils.AssertPresentationAction(
#    "Go to navy", 
#    ["BUG? - speaks 'not selected' apparently due to Down into a table cell",
#     "BRAILLE LINE:  'silver Image yellow Image fuchsia Image navy Image'",
#     "     VISIBLE:  'navy Image', cursor=1",
#     "SPEECH OUTPUT: 'navy not selected'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Left"))
#sequence.append(WaitForFocus("fuchsia", acc_role=pyatspi.ROLE_TABLE_CELL))
#sequence.append(utils.AssertPresentationAction(
#    "Goto fuchsia", 
#    ["BRAILLE LINE:  'silver Image yellow Image fuchsia Image navy Image'",
#     "     VISIBLE:  'fuchsia Image navy Image', cursor=1",
#     "SPEECH OUTPUT: 'fuchsia'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Left"))
#sequence.append(WaitForFocus("yellow", acc_role=pyatspi.ROLE_TABLE_CELL))
#sequence.append(utils.AssertPresentationAction(
#    "Goto yellow", 
#    ["BRAILLE LINE:  'silver Image yellow Image fuchsia Image navy Image'",
#     "     VISIBLE:  'yellow Image fuchsia Image navy ', cursor=1",
#     "SPEECH OUTPUT: 'yellow'"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Escape"))
#sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_PUSH_BUTTON))
#sequence.append(utils.AssertPresentationAction(
#    "Close the Color menu", 
#    ["BUG? - Why does it say Color twice?",
#     "BRAILLE LINE:  'Color Color Menu'",
#     "     VISIBLE:  'Color Color Menu', cursor=1",
#     "SPEECH OUTPUT: 'Color menu'"]))

########################################################################
# Go to the unlabelled buttons
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'Default (below) Above Before After'",
     "     VISIBLE:  'Default (below) Above Before Aft', cursor=1",
     "SPEECH OUTPUT: 'Default (below) menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'Above Before After'",
     "     VISIBLE:  'Above Before After', cursor=1",
     "SPEECH OUTPUT: 'Above menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'Before After'",
     "     VISIBLE:  'Before After', cursor=1",
     "SPEECH OUTPUT: 'Before menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'After'",
     "     VISIBLE:  'After', cursor=1",
     "SPEECH OUTPUT: 'After menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'Default (below) Button'",
     "     VISIBLE:  'Default (below) Button', cursor=1",
     "SPEECH OUTPUT: 'Default (below) button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  ' $lsave options Menu $lsave options Menu $lsave options Menu $lsave options Menu'",
     "     VISIBLE:  'save options Menu $lsave options', cursor=1",
     "SPEECH OUTPUT: 'save options menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'Up Button'",
     "     VISIBLE:  'Up Button', cursor=1",
     "SPEECH OUTPUT: 'Up button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  ' $lsave options Menu $lsave options Menu $lsave options Menu $lsave options Menu'",
     "     VISIBLE:  'save options Menu $lsave options', cursor=1",
     "SPEECH OUTPUT: 'save options menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'Before Button'",
     "     VISIBLE:  'Before Button', cursor=1",
     "SPEECH OUTPUT: 'Before button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  ' $lsave options Menu $lsave options Menu $lsave options Menu $lsave options Menu'",
     "     VISIBLE:  'save options Menu $lsave options', cursor=1",
     "SPEECH OUTPUT: 'save options menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'After Button'",
     "     VISIBLE:  'After Button', cursor=1",
     "SPEECH OUTPUT: 'After button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  ' $lsave options Menu $lsave options Menu $lsave options Menu $lsave options Menu'",
     "     VISIBLE:  'save options Menu', cursor=1",
     "SPEECH OUTPUT: 'save options menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  '  Save Button save options Menu '",
     "     VISIBLE:  '  Save Button save options Menu ', cursor=1",
     "SPEECH OUTPUT: 'Rich Text Test! button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  '  Save Button save options Menu '",
     "     VISIBLE:  '  Save Button save options Menu ', cursor=2",
     "SPEECH OUTPUT: 'Color menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  'Save Button'",
     "     VISIBLE:  'Save Button', cursor=1",
     "SPEECH OUTPUT: 'Save button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  ' $lsave options Menu'",
     "     VISIBLE:  ' $lsave options Menu', cursor=4",
     "SPEECH OUTPUT: 'save options menu'"]))

########################################################################
# Tab to the 1st "Toggle me" toggle button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the next button", 
    ["BRAILLE LINE:  '&=y Toggle me off ToggleButton'",
     "     VISIBLE:  '&=y Toggle me off ToggleButton', cursor=1",
     "BRAILLE LINE:  ' Toggle me  '",
     "     VISIBLE:  ' Toggle me  ', cursor=1",
     "SPEECH OUTPUT: 'Toggle me off toggle button pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:state-changed:pressed",
                           None,
                           None,
                           pyatspi.ROLE_TOGGLE_BUTTON,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Change the 'Toggle me' toggle button", 
    ["BUG? - Why no braille? Actually, there's a similar issue in OOo toggle buttons",
     "SPEECH OUTPUT: 'toggle me on'"]))

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
    ["BRAILLE LINE:  'big Image small Image long  Image tall '",
     "     VISIBLE:  'big Image small Image long  Imag', cursor=1",
     "SPEECH OUTPUT: 'big button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("small", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the small button", 
    ["BUG? - Why no braille here?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'small button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("long", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the long button", 
    ["BUG? - Why no braille here?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'long button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("tall", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the tall button", 
    ["BUG? - Why no braille here?",
     "BRAILLE LINE:  'tall'",
     "     VISIBLE:  'tall', cursor=1",
     "SPEECH OUTPUT: 'tall button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("short", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the short button", 
    ["BUG? - Why no braille here?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'short button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("bit longer", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the bit longer button", 
    ["BUG? - Why no braille here?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'bit longer button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("ridiculously long", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to the ridiculously long button", 
    ["BUG? - Why no braille here?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
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
