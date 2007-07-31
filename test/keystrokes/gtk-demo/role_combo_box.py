#!/usr/bin/python

"""Test of combobox output using the gtk-demo Combo boxes demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running.  Down arrow to the Combo boxes demo and
# invoke it.
#
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Return"))

########################################################################
# When the Combo boxes demo window appears, navigate around them
# 
#sequence.append(WaitForWindowActivate("Combo boxes",None))
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction           (" "))

# "Warning"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0, 0, 0], pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction         ("Down"))

# "New"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0, 0, 2], pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction         ("Return"))

# "New"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction         ("Tab"))

# "Boston"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction         ("Tab"))

# ""
#sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 1], pyatspi.ROLE_TEXT))
sequence.append(TypeAction           ("Four"))
sequence.append(KeyComboAction         ("Tab"))

# ""
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction         ("Tab"))

# "New"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction           (" "))

# "New"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0, 0, 2], pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction         ("Up"))

# "Warning"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0, 0, 0], pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction         ("Return"))

# "Warning"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction         ("Tab"))

# "Boston"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction         ("Tab"))

# ""
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 1], pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction         ("Tab"))

# ""
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction           (" "))

# ""
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 0], pyatspi.ROLE_MENU))
sequence.append(KeyComboAction         ("Down"))

# "One"
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 0, 0], pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction         ("Down"))

# "Two"
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 0, 1], pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction         ("Return"))

# "Two"
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0], pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction         ("<Shift>ISO_Left_Tab"))

########################################################################
# Close the Combo boxes demo
#
# ""
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 1], pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction         ("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Home"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))

sequence.start()
