#!/usr/bin/python

"""Test of automatic presentation of dialog contents using the
   gtk-demo Dialog and Message Boxes demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Dialog and Message Boxes demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Dialog and Message Boxes", 1000))
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the demo is up, wait for focus to appear on the "Message Dialog"
# button and then invoke it.
#
sequence.append(WaitForFocus("Message Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 500))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Information Alert automatic presentation",
    ["BRAILLE LINE:  'gtk-demo Application Information Alert'", 
     "     VISIBLE:  'Information Alert', cursor=1", 
     "BRAILLE LINE:  'gtk-demo Application Information Alert OK Button'", 
     "     VISIBLE:  'OK Button', cursor=1", 
     "SPEECH OUTPUT: 'Information This message box has been popped up the following", 
     "number of times: 1'", 
     "SPEECH OUTPUT: 'OK button'"]))

########################################################################
# Dismiss the information window by activating the OK button.
#
sequence.append(KeyComboAction("Return"))

########################################################################
# Once we're back to the main window of the demo, go to the
# interactive demo, enter some text in the Entry text areas, and
# invoke the Interactive Demo button.
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus("Message Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Interactive Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Testing"))
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Again"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>i", 500))
#sequence.append(WaitForWindowActivate("Interactive Dialog",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(utils.AssertPresentationAction(
    "Interactive Dialog no automatic presentation",
    ["BRAILLE LINE:  'gtk-demo Application Interactive Dialog Dialog'",
     "     VISIBLE:  'Interactive Dialog Dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Interactive Dialog Dialog Entry 1 Testing $l'",
     "     VISIBLE:  'Entry 1 Testing $l', cursor=16",
     "SPEECH OUTPUT: 'Interactive Dialog'",
     "SPEECH OUTPUT: 'Entry 1 text Testing selected'"]))

########################################################################
# Now, do a "Where Am I" in the Interactive Dialog to get the title
# info via KP_Insert+KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Interactive Dialog Where Am I",
    ["BUG? - For some reason, we're not always getting the braille.",
#     "BRAILLE LINE:  'gtk-demo Application Interactive Dialog Dialog Entry 1 Testing $l'",
#     "     VISIBLE:  'Entry 1 Testing $l', cursor=16",
     "SPEECH OUTPUT: 'Interactive Dialog'"]))

########################################################################
# Tab to the OK button and dismiss the window.
#
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction(" "))

########################################################################
# Close the Dialogs demo window
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("<Alt>F4", 500))

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
