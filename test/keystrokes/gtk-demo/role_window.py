#!/usr/bin/python

"""Test of window title output using gtk-demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
# The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application GTK+ Code Demos Frame TabList Widget (double click for demo) ScrollPane TreeTable Widget (double click for demo) ColumnHeader Application main window TREE LEVEL 1'
#      VISIBLE:  'Application main window TREE LEV', cursor=1
#
# SPEECH OUTPUT: 'GTK+ Code Demos frame'
# SPEECH OUTPUT: 'Widget (double click for demo) page'
# SPEECH OUTPUT: 'Widget (double click for demo) column header'
# SPEECH OUTPUT: 'Application main window'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, do a "Where Am I" to get the title info via
# KP_Insert+KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Window Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GTK+ Code Demos Frame TabList Widget (double click for demo) ScrollPane TreeTable Widget (double click for demo) ColumnHeader Application main window TREE LEVEL 1'",
     "     VISIBLE:  'Application main window TREE LEV', cursor=1",
     "SPEECH OUTPUT: 'GTK+ Code Demos'"]))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
