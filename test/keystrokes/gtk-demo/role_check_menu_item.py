#!/usr/bin/python

"""Test of menu checkbox output using the gtk-demo Application Main Window
   demo.
"""

from macaroon.playback import *

sequence = MacroSequence()
import utils

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, go to the Bold check menu item in the
# Preferences menu.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>p"))

sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_MENU))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Bold", acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Bold check item",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar <x> Bold CheckItem\((Control|Primary) b\)'",
     "     VISIBLE:  '<x> Bold CheckItem\((Control|Primary) b\)', cursor=1",
     "SPEECH OUTPUT: 'Bold check item checked (Control|Primary) b'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Bold check item Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar <x> Bold CheckItem\((Control|Primary) b\)'",
     "     VISIBLE:  '<x> Bold CheckItem\((Control|Primary) b\)', cursor=1",
     "SPEECH OUTPUT: 'Preferences'",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Bold'",
     "SPEECH OUTPUT: 'check item checked (Control|Primary) b 4 of 4.'",
     "SPEECH OUTPUT: 'b'"]))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
