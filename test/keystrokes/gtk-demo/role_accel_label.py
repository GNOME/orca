#!/usr/bin/python

"""Test of menu accelerator label output using the gtk-demo UI Manager
   demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Now, invoke the UI Manager demo.
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("UI Manager", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the UI Manager window is up (as indicated by the "close" button
# getting focus), open the File menu via Alt+f
#
#sequence.append(WaitForWindowActivate("UI Manager"))
sequence.append(WaitForFocus("close", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>f"))

########################################################################
# When the "New" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar New(Control n)'
#      VISIBLE:  'New(Control n)', cursor=1
# SPEECH OUTPUT: 'File menu'
# SPEECH OUTPUT: 'New Control n'
#
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar New(Control n)'
#      VISIBLE:  'New(Control n)', cursor=1
# SPEECH OUTPUT: 'File menu'
# SPEECH OUTPUT: 'New'
# SPEECH OUTPUT: 'Control n'
# SPEECH OUTPUT: 'item 1 of 5'
# SPEECH OUTPUT: 'n'
#
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Now, continue on down the menu.
#
# When the "Open" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Open(Control o)'
#      VISIBLE:  'Open(Control o)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Open Control o' 
#
sequence.append(KeyComboAction("Down", 3000))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Save" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Save(Control s)'
#      VISIBLE:  'Save(Control s)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Save Control s'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Save As..." menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Save As...(Control s)'
#      VISIBLE:  'Save As...(Control s)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Save As... Control s'
# 
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Save As...", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Quit" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Quit(Control q)'
#      VISIBLE:  'Quit(Control q)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Quit Control q'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Quit", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Dismiss the menu once we get to the "Quit" menu item and wait for
# the "close" button to get focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("close", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Then, when the menu disappears and the "close" button regains focus,
# Do a "Where Am I" to find the the default button (double
# KP_Insert+KP_Enter).  The following should appear in speech and
# braille (NOTE: you might get speech output for the first press
# of KP_Insert+KP_Enter -- it is OK to ignore that) [[[BUG?: the
# click count doesn't always seem to be calculated correctly -- we
# sometimes get the default button, we sometimes do not]]]:
#
# BRAILLE LINE:  'gtk-demo Application UI Manager Frame close Button'
#      VISIBLE:  'close Button', cursor=1
# SPEECH OUTPUT: 'Default button is close'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

########################################################################
# Activate the "close" button, dismissing the UI Manager demo window.
#
sequence.append(TypeAction(" ", 3000))

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
