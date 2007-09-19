#!/usr/bin/python

"""Test of split pane output using the gtk-demo Paned Widgets demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Paned Widgets demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Paned Widgets", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, go to the split pane.  The following should
# be presented [[[BUG?: No value for speech?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame 60 SplitPane'
#      VISIBLE:  '60 SplitPane', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'split pane'
#
#sequence.append(WaitForWindowActivate("Panes",None))
sequence.append(WaitForFocus("Hi there", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("F8", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SPLIT_PANE))

########################################################################
# Move the split pane to the right.  The following should be presented
# [[[BUG?: No speech output?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame 61 SplitPane'
#      VISIBLE:  '61 SplitPane', cursor=1
#
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("Right", 500))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: No speech output?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame 61 SplitPane'
#      VISIBLE:  '61 SplitPane', cursor=1
#
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Put things back the way they were and close the Panes demo window
#
sequence.append(KeyComboAction("Left"))
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
sequence.append(PauseAction(3000))

sequence.start()
