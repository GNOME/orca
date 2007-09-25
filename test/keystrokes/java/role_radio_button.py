#!/usr/bin/python

"""Test of radio buttons in Java's SwingSet2.
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

##########################################################################
# Tab into check boxes container
#
sequence.append(KeyComboAction("Tab"))

########################################################################
# Expected output when radio button comes into focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Text Radio Buttons Panel & y Radio One  RadioButton'
#      VISIBLE:  '& y Radio One  RadioButton', cursor=1
#
# SPEECH OUTPUT: 'Text Radio Buttons panel'
# SPEECH OUTPUT: 'Radio One  selected radio button'
sequence.append(WaitForFocus("Radio One ", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Expected output when radio button is selected.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Text Radio Buttons Panel &=y Radio One  RadioButton'
#      VISIBLE:  '&=y Radio One  RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'selected'
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(KeyComboAction("Tab"))

########################################################################
# TODO: "selected"?"
# Expected output when radio button comes into focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Text Radio Buttons Panel &=y Radio Two RadioButton'
#      VISIBLE:  '&=y Radio Two RadioButton', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Radio Two selected radio button'
sequence.append(WaitForFocus("Radio Two", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Expected output when radio button is selected.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Text Radio Buttons Panel &=y Radio Two RadioButton'
#      VISIBLE:  '&=y Radio Two RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'selected'
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(KeyComboAction("Tab"))

########################################################################
# Expected output when radio button comes into focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Text Radio Buttons Panel & y Radio Three RadioButton'
#      VISIBLE:  '& y Radio Three RadioButton', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Radio Three selected radio button'
sequence.append(WaitForFocus("Radio Three", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Expected output when radio button is selected.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Text Radio Buttons Panel &=y Radio Three RadioButton'
#      VISIBLE:  '&=y Radio Three RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'selected'
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))
sequence.append(KeyComboAction("Tab"))

########################################################################
# Expected output when radio button comes into focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Image Radio Buttons Panel & y Radio One  RadioButton'
#      VISIBLE:  '& y Radio One  RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'Image Radio Buttons panel'
# SPEECH OUTPUT: 'Radio One  not selected radio button'
sequence.append(WaitForFocus("Radio One ", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# TODO: "item 3 of 3"?
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
# SPEECH OUTPUT: 'Image Radio Buttons'
# SPEECH OUTPUT: 'Radio One radio button'
# SPEECH OUTPUT: 'not selected'
# SPEECH OUTPUT: 'item 3 of 3'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(TypeAction(" "))

########################################################################
# Expected output when radio button is selected.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Image Radio Buttons Panel &=y Radio One  RadioButton'
#      VISIBLE:  '&=y Radio One  RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'selected'
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))

########################################################################
# TODO: "item 3 of 3"?
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
# SPEECH OUTPUT: 'Image Radio Buttons'
# SPEECH OUTPUT: 'Radio One radio button'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: 'item 3 of 3'
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Tab"))

########################################################################
# Expected output when radio button comes into focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Image Radio Buttons Panel &=y Radio Two RadioButton'
#      VISIBLE:  '&=y Radio Two RadioButton', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Radio Two selected radio button'
sequence.append(WaitForFocus("Radio Two", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
# 
# SPEECH OUTPUT: 'Image Radio Buttons'
# SPEECH OUTPUT: 'Radio Two radio button'
# SPEECH OUTPUT: 'not selected'
# SPEECH OUTPUT: 'item 2 of 3'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(TypeAction(" "))

########################################################################
# Expected output when radio button is selected.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Image Radio Buttons Panel &=y Radio Two RadioButton'
#      VISIBLE:  '&=y Radio Two RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'selected'
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
# SPEECH OUTPUT: 'Image Radio Buttons'
# SPEECH OUTPUT: 'Radio Two radio button'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: 'item 2 of 3'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Tab"))

########################################################################
# Expected output when radio button comes into focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Image Radio Buttons Panel & y Radio Three RadioButton'
#      VISIBLE:  '& y Radio Three RadioButton', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Radio Three not selected radio button'
sequence.append(WaitForFocus("Radio Three", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Expected output when radio button is selected.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Radio Buttons TabList Radio Buttons Image Radio Buttons Panel &=y Radio Three RadioButton'
#      VISIBLE:  '&=y Radio Three RadioButton', cursor=1
# 
# SPEECH OUTPUT: 'selected'
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_BUTTON, 5000))

# Tab back up to begining
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
sequence.append(TypeAction           (" "))

sequence.append(PauseAction(3000))

sequence.start()
