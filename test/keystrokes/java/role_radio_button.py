#!/usr/bin/python

"""Test of radio buttons in Java's SwingSet2."""

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
sequence.append(TypeAction(" "))

##########################################################################
# Tab all the way down to the button page tab.
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
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Button Demo", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Tab"))

##########################################################################
# Select Check Boxes tab
#
sequence.append(WaitForFocus("Buttons", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Radio Buttons", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(PauseAction(5000))

##########################################################################
# Tab into check boxes container
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Radio One ", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "1. Move to Radio One radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Text Radio Buttons Panel Text Radio Buttons & y Radio One  RadioButton'",
     "     VISIBLE:  '& y Radio One  RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Text Radio Buttons panel Radio One  not selected radio button'"]))

########################################################################
# Expected output when radio button is selected.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Text Radio Buttons Panel &=y Radio One  RadioButton'
#      VISIBLE:  '&=y Radio One  RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'selected'
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(utils.AssertPresentationAction(
    "2. Select the focused radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Text Radio Buttons Panel Text Radio Buttons &=y Radio One  RadioButton'",
     "     VISIBLE:  '&=y Radio One  RadioButton', cursor=1",
     "SPEECH OUTPUT: 'selected'"]))

########################################################################
# Expected output when radio button comes into focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Radio Two", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "3. Move to Radio Two radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Text Radio Buttons Panel Text Radio Buttons & y Radio Two RadioButton'",
     "     VISIBLE:  '& y Radio Two RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Radio Two not selected radio button'"]))

########################################################################
# Expected output when radio button is selected.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(utils.AssertPresentationAction(
    "4. Select the focused radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Text Radio Buttons Panel Text Radio Buttons &=y Radio Two RadioButton'",
     "     VISIBLE:  '&=y Radio Two RadioButton', cursor=1",
     "SPEECH OUTPUT: 'selected'"]))

########################################################################
# Expected output when radio button comes into focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Radio Three", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "5. Move to Radio Three radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Text Radio Buttons Panel Text Radio Buttons & y Radio Three RadioButton'",
     "     VISIBLE:  '& y Radio Three RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Radio Three not selected radio button'"]))
    
########################################################################
# Expected output when radio button is selected.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(utils.AssertPresentationAction(
    "6. Select the focused radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Text Radio Buttons Panel Text Radio Buttons &=y Radio Three RadioButton'",
     "     VISIBLE:  '&=y Radio Three RadioButton', cursor=1",
     "SPEECH OUTPUT: 'selected'"]))
    
########################################################################
# Expected output when radio button comes into focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Radio One ", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "7. Move to Radio One radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons & y Radio One  RadioButton'",
     "     VISIBLE:  '& y Radio One  RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Image Radio Buttons panel Radio One  not selected radio button'"]))
    
########################################################################
# Basic Where Am I
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "8. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons & y Radio One  RadioButton'",
     "     VISIBLE:  '& y Radio One  RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Image Radio Buttons Radio One  radio button not selected 3 of 3'"]))
    
########################################################################
# Expected output when radio button is selected.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(utils.AssertPresentationAction(
    "9. Select the focused radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons &=y Radio One  RadioButton'",
     "     VISIBLE:  '&=y Radio One  RadioButton', cursor=1",
     "SPEECH OUTPUT: 'selected'"]))
    
########################################################################
# Basic Where Am I
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "10. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons &=y Radio One  RadioButton'",
     "     VISIBLE:  '&=y Radio One  RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Image Radio Buttons Radio One  radio button selected 3 of 3'"]))
    
########################################################################
# Expected output when radio button comes into focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Radio Two", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "11. Move to Radio Two radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons & y Radio Two RadioButton'",
     "     VISIBLE:  '& y Radio Two RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Radio Two not selected radio button'"]))
    
########################################################################
# Basic Where Am I
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "12. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons & y Radio Two RadioButton'",
     "     VISIBLE:  '& y Radio Two RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Image Radio Buttons Radio Two radio button not selected 2 of 3'"]))
    
########################################################################
# Expected output when radio button is selected.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(utils.AssertPresentationAction(
    "13. Select the focused radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons &=y Radio Two RadioButton'",
     "     VISIBLE:  '&=y Radio Two RadioButton', cursor=1",
     "SPEECH OUTPUT: 'selected'"]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "14. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons &=y Radio Two RadioButton'",
     "     VISIBLE:  '&=y Radio Two RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Image Radio Buttons Radio Two radio button selected 2 of 3'"]))
    
########################################################################
# Expected output when radio button comes into focus.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Radio Three", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "15. Move to Radio Three radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons & y Radio Three RadioButton'",
     "     VISIBLE:  '& y Radio Three RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Radio Three not selected radio button'"]))
    
########################################################################
# Expected output when radio button is selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(utils.AssertPresentationAction(
    "16. Select the focused radio button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Radio Buttons TabList Radio Buttons Page Image Radio Buttons Panel Image Radio Buttons &=y Radio Three RadioButton'",
     "     VISIBLE:  '&=y Radio Three RadioButton', cursor=1",
     "SPEECH OUTPUT: 'selected'"]))
    
# Tab back up to beginning
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Paint Border", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Paint Focus", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Enabled", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Content Filled", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Default", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("0", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("10", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

# Toggle the top left button, to return to normal state.
# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
