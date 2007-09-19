#!/usr/bin/python

"""Test of toggle button output using the gtk-demo Expander button demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Expander demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Expander", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, the following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog & y Details ToggleButton'
#      VISIBLE:  '& y Details ToggleButton', cursor=1
#
# SPEECH OUTPUT: 'GtkExpander Expander demo. Click on the triangle for details.'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Details toggle button not pressed'
#
#sequence.append(WaitForWindowActivate("GtkExpander",None))
sequence.append(WaitForFocus("Details", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: pressed state not presented?]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog & y Details ToggleButton'
#      VISIBLE:  '& y Details ToggleButton', cursor=1
#
# SPEECH OUTPUT: 'Details'
# SPEECH OUTPUT: 'toggle button'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Toggle the state of the "Details" button.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog &=y Details ToggleButton'
#      VISIBLE:  '&=y Details ToggleButton', cursor=1
#
# SPEECH OUTPUT: 'pressed'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:state-changed:expanded",
                           "Details",
                           None,
                           pyatspi.ROLE_TOGGLE_BUTTON,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: pressed state not presented?]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog & y Details ToggleButton'
#      VISIBLE:  '&=y Details ToggleButton', cursor=1
#
# SPEECH OUTPUT: 'Details'
# SPEECH OUTPUT: 'toggle button'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Toggle the state of the "Details" button.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog &=y Details ToggleButton'
#      VISIBLE:  '& y Details ToggleButton', cursor=1
#
# SPEECH OUTPUT: 'not pressed'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:state-changed:expanded",
                           "Details",
                           None,
                           pyatspi.ROLE_TOGGLE_BUTTON,
                           5000))

########################################################################
# Close the demo.
#
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Close", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return", 500))

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
