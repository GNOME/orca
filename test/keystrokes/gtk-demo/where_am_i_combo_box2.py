#!/usr/bin/python

"""Test "Where Am I" on comboboxes using the gtk-demo Printing demo, which
gets us a labelled combo box.
"""

from macaroon.playback.keypress_mimic import *

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
sequence.append(TypeAction("Printing", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Printing demo window appears, navigate to the "Only print"
# combobox on the "Page Setup" tab.
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("General", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))

sequence.append(WaitForFocus("Page Setup", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction         ("Tab"))

sequence.append(WaitForFocus("All sheets", acc_role=pyatspi.ROLE_COMBO_BOX))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("Down"))
# Do "where am i"
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("Down", 500))
# Do "where am i"
sequence.append(KeyComboAction("KP_Enter"))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction         ("<Alt>c", 500))

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
