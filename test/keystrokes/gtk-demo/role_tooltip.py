#!/usr/bin/python

"""Test of tooltips using the gtk-demo Application Main Window demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table.
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo.
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, press Ctrl+F1 to pop up the tooltip.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Show Open tooltip",
    ["BRAILLE LINE:  'Open a file'",
     "     VISIBLE:  'Open a file', cursor=0",
     "SPEECH OUTPUT: 'Open a file'"]))

########################################################################
# Dismiss the tooltip.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Hide Open tooltip",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'",
     "     VISIBLE:  'Open Button', cursor=1",
     "SPEECH OUTPUT: 'Open'",
     "SPEECH OUTPUT: 'button'"]))

########################################################################
# Move on to the Quit button.  Check its tooltip.
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Quit", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Show Quit tooltip",
    ["BRAILLE LINE:  'Quit'",
     "     VISIBLE:  'Quit', cursor=0",
     "SPEECH OUTPUT: 'Quit'"]))

########################################################################
# Dismiss the tooltip.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Hide Quit tooltip",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Quit Button'",
     "     VISIBLE:  'Quit Button', cursor=1",
     "SPEECH OUTPUT: 'Quit'",
     "SPEECH OUTPUT: 'button'"]))

########################################################################
# Move on to the GTK! button.  Check its tooltip.
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("GTK!", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Show GTK+ tooltip",
    ["BRAILLE LINE:  'GTK+'",
     "     VISIBLE:  'GTK+', cursor=0",
     "SPEECH OUTPUT: 'GTK+'"]))

########################################################################
# Dismiss the tooltip.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(WaitAction("object:state-changed:visible",
                           None,
                           None,
                           pyatspi.ROLE_TOOL_TIP,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Hide GTK+ tooltip",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar GTK! Button'",
     "     VISIBLE:  'GTK! Button', cursor=1",
     "SPEECH OUTPUT: 'GTK!'",
     "SPEECH OUTPUT: 'button'"]))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
sequence.append(KeyComboAction("<Alt>F4", 500))
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
