#!/usr/bin/python

"""Test "Where Am I" on comboboxes using the gtk-demo Combo boxes demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Combo boxes demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Combo boxes", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Combo boxes demo window appears, do a "where am I" on them
# 
#sequence.append(WaitForWindowActivate("Combo boxes",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Now do detailed information "where am i", double press KP_Enter.
# But first, wait 3 seconds.

sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Select a different item.
sequence.append(TypeAction(" ", 2000))
sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Return"))

########################################################################
# Repeate where am i on combobox with newly selected item.
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("KP_Enter"))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))


sequence.append(KeyComboAction("Tab", 2000))
########################################################################
# Do "where am I" on another combobox. This one has a 2 level hierarchy.
# TODO: "where am I" does not show the correct state of the combo box. It 
# seems like the name of the selected child of the combobox is used, but this
# is not sufficient since there are multiple hierarchies. Probably
# the right way of doing this is to use the accessible's name, since 
# unfortunately the child "menu items" are unlabled. A GAIL bug, must submit.
sequence.append(WaitForFocus("Boston", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("KP_Enter"))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("Tab", 2000))

########################################################################
# Enter text that exists in the combo box options.
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Two"))
sequence.append(KeyComboAction("Tab", 500))

########################################################################
# Do where am I on another combobox. This is a text entry combobox.
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("KP_Enter"))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Go back and enter text that does not exist in the combo box options. 
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Four"))
sequence.append(KeyComboAction("Tab", 500))

# Go back to combo box.
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("KP_Enter"))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Close the Combo boxes demo
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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
