#!/usr/bin/python

"""Test of tear off menu item output using the gtk-demo menus demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the menus demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Menus", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the menus demo window appears, go to the tear off menu item.
# 
#sequence.append(WaitForWindowActivate("menus",None))
sequence.append(WaitForFocus("Flip", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("F10"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("item  2 - 1",
                             acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEAROFF_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Tear off menu item",
    ["BRAILLE LINE:  'gtk-demo Application Menus Frame MenuBar TearOffMenuItem'",
     "     VISIBLE:  'TearOffMenuItem', cursor=1",
     "SPEECH OUTPUT: 'tear off menu item'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Tear off menu item Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Menus Frame MenuBar TearOffMenuItem'",
     "     VISIBLE:  'TearOffMenuItem', cursor=1",
     "SPEECH OUTPUT: 'tear off menu item'"]))

########################################################################
# Get out of the menu and close the menus demo window.
#
sequence.append(KeyComboAction("F10"))

sequence.append(WaitForFocus("Flip", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Close", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return", 500))

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
