#!/usr/bin/python

"""Test of toolbar output using the gtk-demo Application Main Window
   demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, the following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'
#      VISIBLE:  'Open Button', cursor=1
#
# SPEECH OUTPUT: 'Application Window frame'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Open button'
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: should we present the fact that we're in a toolbar?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'
#      VISIBLE:  'Open Button', cursor=1
#
# SPEECH OUTPUT: 'Open'
# SPEECH OUTPUT: 'button'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Arrow Right to the triangular button next to the "Open" button.  The
# following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar & y ToggleButton'
#      VISIBLE:  '& y ToggleButton', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'toggle button not pressed'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: should we present the fact that we're in a toolbar?]]]
# [[[BUG?: we don't present the toggle button state]]]:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar & y ToggleButton'
#      VISIBLE:  '& y ToggleButton', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'toggle button'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Arrow Right to the the "Quit" button.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Quit Button'
#      VISIBLE:  'Quit Button', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Quit button'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Quit", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: should we present the fact that we're in a toolbar?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Quit Button'
#      VISIBLE:  'Quit Button', cursor=1
#
# SPEECH OUTPUT: 'Quit'
# SPEECH OUTPUT: 'button'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Close the Application Window demo window
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
