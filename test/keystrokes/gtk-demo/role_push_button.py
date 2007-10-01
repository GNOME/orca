#!/usr/bin/python

"""Test of page tab output using the gtk-demo Printing demo
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Printing demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Button Boxes", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Button Boxes demo window appears, the following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Spread Panel OK Button'
#      VISIBLE:  'OK Button', cursor=1
#
# SPEECH OUTPUT: 'Button Boxes frame'
# SPEECH OUTPUT: 'Horizontal Button Boxes panel Spread panel'
# SPEECH OUTPUT: 'OK button'
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Spread Panel OK Button'
#      VISIBLE:  'OK Button', cursor=1
#
# SPEECH OUTPUT: 'OK'
# SPEECH OUTPUT: 'button'
# SPEECH OUTPUT: ' Alt o'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Tab to the Cancel button.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Spread Panel Cancel Button'
#      VISIBLE:  'Cancel Button', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Cancel button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Cancel", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Tab to the next "OK" button in the "Edge" panel.  The following should
# be presented:
#
# BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Edge Panel OK Button'
#      VISIBLE:  'OK Button', cursor=1
#      
# SPEECH OUTPUT: 'Edge panel'
# SPEECH OUTPUT: 'OK button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Help", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Close the demo
#
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
