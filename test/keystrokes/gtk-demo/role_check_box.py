#!/usr/bin/python

"""Test of checkbox output using the gtk-demo Paned Widgets demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Paned Widgets demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Paned Widgets"))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, interact with a few check boxes
#
#sequence.append(WaitForWindowActivate("Panes",None))
# "Hi there"
sequence.append(WaitForFocus("Hi there", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Shrink", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Shrink", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))

########################################################################
# Close the Panes demo window
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

sequence.start()
