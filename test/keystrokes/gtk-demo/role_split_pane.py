#!/usr/bin/python

"""Test of split pane output using the gtk-demo Paned Widgets demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Paned Widgets demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Paned Widgets"))
sequence.append(KeyComboAction("Return", 500))

sequence.append(KeyComboAction("Return", 500))
sequence.append(PauseAction(1000))

########################################################################
# When the demo comes up, go to the split pane.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F8", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SPLIT_PANE))
sequence.append(utils.AssertPresentationAction(
    "Split pane",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame 74 SplitPane'",
     "     VISIBLE:  '74 SplitPane', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Panes Frame 74 SplitPane'",
     "     VISIBLE:  '74 SplitPane', cursor=1",
     "SPEECH OUTPUT: 'split pane 74'",
     "SPEECH OUTPUT: '74'"]))

########################################################################
# Move the split pane to the right.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SPLIT_PANE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Split pane increment value",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame 75 SplitPane'",
     "     VISIBLE:  '75 SplitPane', cursor=1",
     "SPEECH OUTPUT: '75'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Split pane Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame 75 SplitPane'",
     "     VISIBLE:  '75 SplitPane', cursor=1",
     "SPEECH OUTPUT: 'split pane 75'"]))

########################################################################
# Put things back the way they were
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SPLIT_PANE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Split pane decrement value",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame 74 SplitPane'",
     "     VISIBLE:  '74 SplitPane', cursor=1",
     "SPEECH OUTPUT: '74'"]))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
sequence.append(KeyComboAction("<Alt>F4", 500))
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
