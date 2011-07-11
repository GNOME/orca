#!/usr/bin/python

"""Test of menu, menu navigation, and menu item output using the
   gtk-demo Application Main Window demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

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
# When the demo comes up, open the File menu via F10.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("F10"))
sequence.append(WaitForFocus("File",
                             acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "File menu",
    ["KNOWN ISSUE - Gtk+ 3 stopped giving us expected events for the first selected/focused item in a menu when the menu is first opened. This is not new to the Gail integration into Gtk+",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "SPEECH OUTPUT: 'File menu'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "File menu Where Am I",
    ["KNOWN ISSUE - Gtk+ 3 stopped giving us expected events for the first selected/focused item in a menu when the menu is first opened. This is not new to the Gail integration into Gtk+",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "SPEECH OUTPUT: 'menu bar",
     "SPEECH OUTPUT: 'File'",
     "SPEECH OUTPUT: 'menu 1 of 3.'",
     "SPEECH OUTPUT: 'f'"]))

########################################################################
# Right arrow to the "Preferences" menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Preferences",
                             acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Preferences menu",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame Preferences Menu'",
     "     VISIBLE:  'Preferences Menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Preferences menu Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame Preferences Menu'",
     "     VISIBLE:  'Preferences Menu', cursor=1",
     "SPEECH OUTPUT: 'menu bar",
     "SPEECH OUTPUT: 'Preferences",
     "SPEECH OUTPUT: 'menu 2 of 3.",
     "SPEECH OUTPUT: 'p'"]))

########################################################################
# Go down to the "Color" menu.
#
sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Color",
                             acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Color menu",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Color Menu'",
     "     VISIBLE:  'Color Menu', cursor=1",
     "SPEECH OUTPUT: 'Color menu'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Color menu Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Color Menu'",
     "     VISIBLE:  'Color Menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Color'",
     "SPEECH OUTPUT: 'menu 2 of 4.'",
     "SPEECH OUTPUT: 'c'"]))

########################################################################
# Go down to the "Shape" menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Shape",
                             acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Shape menu",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Shape Menu'",
     "     VISIBLE:  'Shape Menu', cursor=1",
     "SPEECH OUTPUT: 'Shape menu'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Shape menu Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Shape Menu'",
     "     VISIBLE:  'Shape Menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Shape'",
     "SPEECH OUTPUT: 'menu 3 of 4.'",
     "SPEECH OUTPUT: 's'"]))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("F10"))
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
