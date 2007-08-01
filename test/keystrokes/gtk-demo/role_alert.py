#!/usr/bin/python

"""Test of automatic presentation of dialog contents using the
   gtk-demo Dialog and Message Boxes demo.
"""

from macaroon.playback.keypress_mimic import *

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
# Once the demo is up, invoke the Message Dialog button and then close
# the resulting "This message has been popped up..."  dialog window by
# pressing it's OK button.
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus("Message Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return", 500))

#sequence.append(WaitForWindowActivate("Information",None))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once we're back to the main window of the demo, go to the
# interactive demo, enter some text in the Entry text areas, and
# invoke the Interactive Demo button.
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
# "Message Dialog"
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
# When the Interactive Dialog demo is up, tab to the OK button and
# dismiss the window
#
#sequence.append(WaitForWindowActivate("Interactive Dialog",None))
# ""
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
