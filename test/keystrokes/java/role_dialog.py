#!/usr/bin/python

"""Test of dialogs in Java's SwingSet2.
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
# Tab over to the JOptionPane demo, and activate it.
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
sequence.append(TypeAction(" "))

##########################################################################
# Tab down to the dialog activation button in the demo.
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
sequence.append(WaitForFocus("Option Pane Demo", acc_role=pyatspi.ROLE_PAGE_TAB))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Input Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# TODO: Shouldn't braille also read the label?
# Expected output when "Input" dialog is activated
# 
# BRAILLE LINE:  'SwingSet2 Application Input Dialog'
#      VISIBLE:  'Input Dialog', cursor=1
# 
# SPEECH OUTPUT: 'Input What is your favorite movie?'
# sequence.append(WaitForWindowActivate("Input",None))

########################################################################
# Expected output when the text input field gets focus.
#
# BRAILLE LINE:  'SwingSet2 Application Input Dialog RootPane LayeredPane OptionPane  $l'
#      VISIBLE:  ' $l', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'text '
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

########################################################################
# Type the best movie ever, and press return.
sequence.append(TypeAction("RoboCop"))
sequence.append(KeyComboAction("Return"))

########################################################################
# TODO: Shouldn't braille also read the label?
# Expected output when "Message" dialog gets activated.
# 
# BRAILLE LINE:  'SwingSet2 Application Message Dialog'
#      VISIBLE:  'Message Dialog', cursor=1
# 
# SPEECH OUTPUT: 'Message RoboCop: That was a pretty good movie!'
# sequence.append(WaitForWindowActivate("Message",None))

########################################################################
# Expected output when "OK" button gets focus.
# 
# BRAILLE LINE:  'SwingSet2 Application Message Dialog RootPane LayeredPane Alert OK Button'
#      VISIBLE:  'OK Button', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'OK button'
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# TODO: Is where am i giving enough?
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'OK'
# SPEECH OUTPUT: 'button'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))


########################################################################
# Press return to close dialog.
sequence.append(KeyComboAction("Return"))

########################################################################
# Wait for main application to gain focus and return to starting state.
# sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("Show Input Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Warning Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Message Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Component Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Confirmation Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))


# Toggle the top left button, to return to normal state.
sequence.append(TypeAction           (" "))

sequence.append(PauseAction(3000))

sequence.start()
