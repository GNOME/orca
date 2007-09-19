#!/usr/bin/python

"""Test of automatic presentation of dialog contents using the
   gtk-demo Dialog and Message Boxes demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Dialog and Message Boxes demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Dialog and Message Boxes", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the demo is up, wait for focus to appear on the "Message Dialog"
# button.  The following should be presented in speech and braille,
# where the name of the "Dialogs" border is spoken when the button
# gets focus:
#
# BRAILLE LINE:  'gtk-demo Application Dialogs Frame Dialogs Dialogs Panel Message Dialog Button'
#      VISIBLE:  'Message Dialog Button', cursor=1
#
# SPEECH OUTPUT: 'Dialogs panel'
# SPEECH OUTPUT: 'Message Dialog button'
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus("Message Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Now invoke the "Message Dialog" button.  When the window appears,
# the following should be presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Information Alert OK Button'
#      VISIBLE:  'OK Button', cursor=1
#
# SPEECH OUTPUT: 'Information This message box has been popped up the following
# number of times: 1'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'OK button'
#
sequence.append(KeyComboAction("Return", 500))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the information window by activating the OK button.
#
sequence.append(KeyComboAction("Return"))

########################################################################
# Once we're back to the main window of the demo, go to the
# interactive demo, enter some text in the Entry text areas, and
# invoke the Interactive Demo button.
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus("Message Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Interactive Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Testing"))
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Again"))
sequence.append(KeyComboAction("<Alt>i", 500))

########################################################################
# When the Interactive Dialog demo comes up, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Interactive Dialog Dialog Entry 1 Testing $l'
#      VISIBLE:  'Entry 1 Testing $l', cursor=16
#
# SPEECH OUTPUT: 'Interactive Dialog'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Entry 1 text Testing'
# SPEECH OUTPUT: 'Testing'
# SPEECH OUTPUT: 'selected'
#
#sequence.append(WaitForWindowActivate("Interactive Dialog",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))

########################################################################
# Now, do a "Where Am I" in the Interactive Dialog to get the title
# info via KP_Insert+KP_Enter.  The following should be presented in
# speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Interactive Dialog Dialog Entry 1 Testing $l'
#      VISIBLE:  'Entry 1 Testing $l', cursor=16
#
# SPEECH OUTPUT: 'Interactive Dialog'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

########################################################################
# Tab to the OK button and dismiss the window.
#
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Close the Dialogs demo window
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
