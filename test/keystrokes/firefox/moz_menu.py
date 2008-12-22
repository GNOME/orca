#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Test of Mozilla ARIA menu presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Accessible DHTML" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the Mozilla ARIA spreadsheet demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/spreadsheet"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("ARIA Spreadsheet and Menubar", 
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Move to the menu.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Alt>m"))
sequence.append(utils.AssertPresentationAction(
    "Move to the menu", 
    ["BRAILLE LINE:  'Edit'",
     "     VISIBLE:  'Edit', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Edit'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Edit'",
     "     VISIBLE:  'Edit', cursor=1",
     "SPEECH OUTPUT: 'Edit section'",
     "SPEECH OUTPUT: 'Edit'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'item 1 of 1'"]))

########################################################################
# Use arrows to navigate menu structure.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move to View", 
    ["BRAILLE LINE:  'Edit View'",
     "     VISIBLE:  'Edit View', cursor=6",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'View'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(PauseAction(2000))
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to Themes", 
    ["BRAILLE LINE:  'Themes          >'",
     "     VISIBLE:  'Themes          >', cursor=(0|1)",
     "BRAILLE LINE:  'Themes          >'",
     "     VISIBLE:  'Themes          >', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Themes          >'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(PauseAction(2000))
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move to basic grey", 
    ["BRAILLE LINE:  'Basic Grey'",
     "     VISIBLE:  'Basic Grey', cursor=0",
     "BRAILLE LINE:  'Basic Grey'",
     "     VISIBLE:  'Basic Grey', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Basic Grey'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to the blues", 
    ["BRAILLE LINE:  'The Blues'",
     "     VISIBLE:  'The Blues', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'The Blues'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to garden", 
    ["BRAILLE LINE:  'Garden'",
     "     VISIBLE:  'Garden', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Garden'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to in the pink", 
    ["BRAILLE LINE:  'In the Pink grayed'",
     "     VISIBLE:  'In the Pink grayed', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'In the Pink grayed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to rose", 
    ["BRAILLE LINE:  'Rose'",
     "     VISIBLE:  'Rose', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Rose'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Move back to Themes", 
    ["BRAILLE LINE:  'Themes          >'",
     "     VISIBLE:  'Themes          >', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Themes          >'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to hide", 
    ["BRAILLE LINE:  'Hide'",
     "     VISIBLE:  'Hide', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Hide'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to show", 
    ["BRAILLE LINE:  'Show'",
     "     VISIBLE:  'Show', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to more", 
    ["BRAILLE LINE:  'More                >'",
     "     VISIBLE:  'More                >', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'More                >'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Move to one", 
    ["BRAILLE LINE:  'one'",
     "     VISIBLE:  'one', cursor=0",
     "BRAILLE LINE:  'one'",
     "     VISIBLE:  'one', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move to two", 
    ["BRAILLE LINE:  'two'",
     "     VISIBLE:  'two', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "leave menu", 
    ["BRAILLE LINE:  'Entry # Date Expense Amount Merchant Type'",
     "     VISIBLE:  'Entry # Date Expense Amount Merc', cursor=8",
     "SPEECH OUTPUT: 'Entry # text Date text Expense text Amount text Merchant text Type column header'"]))

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
