#!/usr/bin/python

"""Test of status bar output using the gtk-demo Application Main Window
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
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, do a "Where Am I" to get the status bar info
# via double KP_Insert+KP_Enter.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Status bar Where Am I",
    ["BRAILLE LINE:  'Application Window'",
     "     VISIBLE:  'Application Window', cursor=0",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'",
     "     VISIBLE:  'Open Button', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'",
     "     VISIBLE:  'Open Button', cursor=1",
     "BRAILLE LINE:  'Cursor at row 0 column 0 - 0 chars in document'",
     "     VISIBLE:  'Cursor at row 0 column 0 - 0 cha', cursor=0",
     "SPEECH OUTPUT: 'Application Window'",
     "SPEECH OUTPUT: 'Cursor at row 0 column 0 - 0 chars in document'"]))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("<Alt>F4"))

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
