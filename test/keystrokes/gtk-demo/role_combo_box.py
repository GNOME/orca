#!/usr/bin/python

"""Test of combobox output using the gtk-demo Combo boxes demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Combo boxes demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Combo boxes"))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Combo boxes demo window appears, navigate around them
# 
#sequence.append(WaitForWindowActivate("Combo boxes",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Boston", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Four"))
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Boston", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("One", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))

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

sequence.start()
