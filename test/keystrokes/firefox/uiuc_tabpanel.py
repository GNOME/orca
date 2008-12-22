#!/usr/bin/python

"""Test of UIUC tab panel presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Tab Panel Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/tabpanel/tabpanel1.php"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Navigate to second tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to second tab", 
    ["BRAILLE LINE:  'TabList TabList TabList TabList Crust Page Veges Page Carnivore Page Delivery Page'",
     "     VISIBLE:  'Veges Page Carnivore Page Delive', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Veges page'"]))
    
########################################################################
# Navigate to third tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to third tab", 
    ["BRAILLE LINE:  'TabList TabList TabList TabList Crust Page Veges Page Carnivore Page Delivery Page'",
     "     VISIBLE:  'Carnivore Page Delivery Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Carnivore page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'TabList TabList TabList TabList Crust Page Veges Page Carnivore Page Delivery Page'",
     "     VISIBLE:  'Carnivore Page Delivery Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Carnivore page'",
     "SPEECH OUTPUT: 'item 3 of 4'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Navigate to fourth tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to fourth tab", 
    ["BRAILLE LINE:  'TabList TabList TabList TabList Crust Page Veges Page Carnivore Page Delivery Page'",
     "     VISIBLE:  'Delivery Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Delivery page'"]))
    
########################################################################
# Navigate back to third tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to back to third tab", 
    ["BRAILLE LINE:  'TabList TabList TabList TabList Crust Page Veges Page Carnivore Page Delivery Page'",
     "     VISIBLE:  'Carnivore Page Delivery Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Carnivore page'"]))
     
########################################################################
# Tab into third page
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab into third page", 
    ["BRAILLE LINE:  '< > CheckBox Hamburger'",
     "     VISIBLE:  '< > CheckBox Hamburger', cursor=1",
     "SPEECH OUTPUT: 'Carnivore scroll pane'",
     "SPEECH OUTPUT: 'Hamburger check box not checked'"]))
    
########################################################################
# Press the checkbox
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction           ("  "))
sequence.append(utils.AssertPresentationAction(
    "press checkbox", 
    ["BRAILLE LINE:  '<x> CheckBox Hamburger'",
     "     VISIBLE:  '<x> CheckBox Hamburger', cursor=1",
     "BRAILLE LINE:  '< > CheckBox Hamburger'",
     "     VISIBLE:  '< > CheckBox Hamburger', cursor=1",
     "SPEECH OUTPUT: 'checked'",
     "SPEECH OUTPUT: 'not checked'"]))

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
