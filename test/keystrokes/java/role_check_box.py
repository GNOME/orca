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
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Check Boxes", acc_role=pyatspi.ROLE_PAGE_TAB))

##########################################################################
# Tab into check boxes container
#
sequence.append(KeyComboAction("Tab"))

########################################################################
# When the "One" checkbox gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Check Boxes TabList Check Boxes Text CheckBoxes Panel <x> One  CheckBox'
#      VISIBLE:  '<x> One  CheckBox', cursor=1
# 
# SPEECH OUTPUT: 'Text CheckBoxes panel'
# SPEECH OUTPUT: 'One  check box not checked'

sequence.append(WaitForFocus("One ", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'One check box'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Now, change its state.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Horizontal Panel <x> Resize CheckBox'
#      VISIBLE:  '<x> Resize CheckBox', cursor=1
#
# SPEECH OUTPUT: 'checked'
#
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX,5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'One check box'
# SPEECH OUTPUT: 'checked'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Change the state back and move on to a few more check boxes.  The
# presentation in speech and braille should be similar to the above.
#
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Three", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))

########################################################################
# When the "One" checkbox gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Check Boxes TabList Check Boxes Text CheckBoxes Panel <x> One  CheckBox'
#      VISIBLE:  '<x> One  CheckBox', cursor=1
# 
# SPEECH OUTPUT: 'Text CheckBoxes panel'
# SPEECH OUTPUT: 'One  check box not checked'
sequence.append(WaitForFocus("One ", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'One check box'
# SPEECH OUTPUT: 'checked'
# SPEECH OUTPUT: ''

sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Change the state back and move on to a few more check boxes.  The
# presentation in speech and braille should be similar to the above.
#
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Three", acc_role=pyatspi.ROLE_CHECK_BOX))
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
