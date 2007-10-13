#!/usr/bin/python

"""Test of icon output using the gtk-demo Icon View Basics demo under
   the Icon View area.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Icon View Basics demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View Basics", 1000))
sequence.append(KeyComboAction("Return", 500))

sequence.append(utils.StartRecordingAction())
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_LAYERED_PANE))
sequence.append(utils.AssertPresentationAction(
    "Layered pane focus",
    ["BUG? - should something be presented here?"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Layered pane Where Am I",
    ["BUG? - should we present the number of items in the layered pane?",
     "BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane'",
     "     VISIBLE:  'LayeredPane', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'layered pane'"]))

########################################################################
# Down into the icon list, finally making something be selected in the
# view.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))
sequence.append(utils.AssertPresentationAction(
    "bin icon",
    ["BUG? - we cannot get reliable output from this test since it depends on the contents of /",
     "BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane Desktop Icon'",
     "     VISIBLE:  'Desktop Icon', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Desktop icon'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "bin icon Where Am I",
    ["BUG? - we cannot get reliable output from this test since it depends on the contents of /",
     "BUG? - the icon is shown as selected, so we should present 1 of 26 items selected."]))

########################################################################
# Arrow right and wait for the next icon to be selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))
sequence.append(utils.AssertPresentationAction(
    "boot icon",
    ["BUG? - we cannot get reliable output from this test since it depends on the contents of /"]))

########################################################################
# Select more than one icon by doing Shift+Right.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Right", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))
sequence.append(utils.AssertPresentationAction(
    "icon selection",
    ["BUG? - we cannot get reliable output from this test since it depends on the contents of /",
     "BUG? - we do not announce selection of icons when they are selected."]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "icon selection Where Am I",
    ["BUG? - we cannot get reliable output from this test since it depends on the contents of /",
     "BUG? - we do not announce selection of icons (e.g., 2 of 26 items selected)."]))

########################################################################
# Close the GtkIconView demo window
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("<Control>f"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
