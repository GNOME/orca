#!/usr/bin/python

"""Test of dialogs in Java's SwingSet2."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

# Wait for entire window to get populated.
sequence.append(PauseAction(5000))

##########################################################################
# Tab over to the JOptionPane demo, and activate it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(TypeAction(" "))

##########################################################################
# Tab down to the dialog activation button in the demo.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Option Pane Demo", acc_role=pyatspi.ROLE_PAGE_TAB))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Input Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Dialog is activated
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(utils.AssertPresentationAction(
    "1. Dialog is activated",
    ["BRAILLE LINE:  'SwingSet2 Application Input Dialog'",
     "     VISIBLE:  'Input Dialog', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'Input What is your favorite movie?'",
     "SPEECH OUTPUT: 'text '"]))

########################################################################
# Type the best movie ever, and press return.
#
sequence.append(PauseAction(3000))
sequence.append(TypeAction("RoboCop"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Return"))

########################################################################
# Expected output when "OK" button gets focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "2. OK button gains focus",
    ["BUG? - We don't always present anything here. Need to investigate.",
     "BRAILLE LINE:  'SwingSet2 Application Message Dialog RootPane LayeredPane Alert OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 frame 1 unfocused dialog'",
     "SPEECH OUTPUT: 'Option Pane Demo tab list Option Pane Demo page Show Input Dialog button'",
     "SPEECH OUTPUT: 'Message RoboCop: That was a pretty good movie!'",
     "SPEECH OUTPUT: 'OK button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "3. Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application Message Dialog RootPane LayeredPane Alert OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'OK button'"]))

########################################################################
# Press return to close dialog.
sequence.append(KeyComboAction("Return"))

########################################################################
# Wait for main application to gain focus and return to starting state.
# sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("Show Input Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Warning Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Message Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Component Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show Confirmation Dialog", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))


# Toggle the top left button, to return to normal state.
sequence.append(TypeAction(" "))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
