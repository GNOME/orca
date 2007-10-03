#!/usr/bin/python

"""Test of tooltips using the gtk-demo Application Main Window demo.
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
# When the demo comes up, press Ctrl+F1 to pop up the tooltip.  The
# following should be presented:
#
# BRAILLE LINE:  'Open a file'
#      VISIBLE:  'Open a file', cursor=0
#
# SPEECH OUTPUT: 'Open a file'
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))

########################################################################
# Dismiss the tooltip.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'
#      VISIBLE:  'Open Button', cursor=1
#
# SPEECH OUTPUT: 'Open button'
#
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))

########################################################################
# Move on to the Quit button.  Check its tooltip.  The following should
# be presented:
#
# BRAILLE LINE:  'Quit'
#      VISIBLE:  'Quit', cursor=0
#
# SPEECH OUTPUT: 'Quit'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Quit", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))

########################################################################
# Dismiss the tooltip.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Quit Button'
#      VISIBLE:  'Quit Button', cursor=1
#
# SPEECH OUTPUT: 'Quit button'
#
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))

########################################################################
# Move on to the GTK! button.  Check its tooltip.  The following should
# be presented:
#
# BRAILLE LINE:  'GTK+'
#      VISIBLE:  'GTK+', cursor=0
#
# SPEECH OUTPUT: 'GTK+'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("GTK!", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))

########################################################################
# Dismiss the tooltip.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar GTK! Button'
#      VISIBLE:  'GTK! Button', cursor=1
#
# SPEECH OUTPUT: 'GTK! button'
#
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
sequence.append(KeyComboAction("<Alt>F4", 500))
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
