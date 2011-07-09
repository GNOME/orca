#!/usr/bin/python

"""Test of menu accelerator label output using the gtk-demo UI Manager
   demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

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

# For some reason we're not getting the events we need to present the
# first item in a menu. This is new to Gtk+ 3, but not to the Gail
# integration into Gtk+. This Down+Up hack will trigger what we need
# for this test in the meantime.
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Up"))

sequence.append(utils.StartRecordingAction())
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "New menu item",
    ["BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar New(Control n)'",
     "     VISIBLE:  'New(Control n)', cursor=1",
     "SPEECH OUTPUT: 'New Control n'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "New menu item Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar New(Control n)'",
     "     VISIBLE:  'New(Control n)', cursor=1",
     "SPEECH OUTPUT: 'File'",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'New'",
     "SPEECH OUTPUT: 'Control n 1 of 5.'",
     "SPEECH OUTPUT: 'n'"]))

########################################################################
# Now, continue on down the menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Open menu item",
    ["BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Open(Control o)'",
     "     VISIBLE:  'Open(Control o)', cursor=1",
     "SPEECH OUTPUT: 'Open Control o'"]))

########################################################################
# Now, continue on down the menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Save menu item",
    ["BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Save(Control s)'",
     "     VISIBLE:  'Save(Control s)', cursor=1",
     "SPEECH OUTPUT: 'Save Control s'"]))

########################################################################
# Now, continue on down the menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Save As...", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Save As... menu item",
    ["BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Save As...(Control s)'",
     "     VISIBLE:  'Save As...(Control s)', cursor=1",
     "SPEECH OUTPUT: 'Save As... Control s'"]))

########################################################################
# Now, continue on down the menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Quit", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Quit menu item",
    ["BRAILLE LINE:  'gtk-demo Application UI Manager Frame MenuBar Quit(Control q)'",
     "     VISIBLE:  'Quit(Control q)', cursor=1",
     "SPEECH OUTPUT: 'Quit Control q'"]))

########################################################################
# Dismiss the menu once we get to the "Quit" menu item and wait for
# the "close" button to get focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("close", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Then, when the menu disappears and the "close" button regains focus,
# Do a "Where Am I" to find the the default button (double
# KP_Insert+KP_Enter).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Where Am I default button",
    ["BRAILLE LINE:  'UI Manager'",
     "     VISIBLE:  'UI Manager', cursor=0",
     "BRAILLE LINE:  'gtk-demo Application UI Manager Frame close Button'",
     "     VISIBLE:  'close Button', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application UI Manager Frame close Button'",
     "     VISIBLE:  'close Button', cursor=1",
     "BRAILLE LINE:  'Default button is close'",
     "     VISIBLE:  'Default button is close', cursor=0",
     "SPEECH OUTPUT: 'UI Manager'",
     "SPEECH OUTPUT: 'Default button is close'"]))

########################################################################
# Activate the "close" button, dismissing the UI Manager demo window.
#
sequence.append(TypeAction(" "))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))

sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
