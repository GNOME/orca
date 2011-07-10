#!/usr/bin/python

"""Test of label presentation using the gtk-demo
   Dialog and Message Boxes demo.
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
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the demo is up, invoke the Message Dialog button.
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus("Message Dialog",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return", 500))

sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Tab to the "This message box..." label.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitAction("object:state-changed:focused",
                           None,
                           None,
                           pyatspi.ROLE_LABEL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "This message box label",
    ["BRAILLE LINE:  'number of times: $l'",
     "     VISIBLE:  'number of times: $l', cursor=17",
     "BRAILLE LINE:  'number of times: $l'",
     "     VISIBLE:  'number of times: $l', cursor=17",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times: selected label'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "This message box label Where Am I",
    ["BRAILLE LINE:  'number of times: $l'",
     "     VISIBLE:  'number of times: $l', cursor=17",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times:'",
     "SPEECH OUTPUT: 'selected label'"]))

########################################################################
# Do an extended "Where Am I" via double KP_Enter.
#
# JD to WDW: The difference here is that we are not repeating the speech
# output. Personally I think that's a good thing. Is there any reason
# we should be duplicating output in the case of a detailed/extended
# where am i?
#
# WDW to JD: the first should be for the first KP_Enter (i.e., basic
# where am I) and the second should be for the second KP_Enter (i.e.,
# extended where am I). So, why did we end up losing one?
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "This message box label Extended Where Am I",
    ["BRAILLE LINE:  'number of times: $l'",
     "     VISIBLE:  'number of times: $l', cursor=17",
     "BRAILLE LINE:  'number of times: $l'",
     "     VISIBLE:  'number of times: $l', cursor=17",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times:'",
     "SPEECH OUTPUT: 'selected label'"]))

########################################################################
# Position the caret at the beginning of the label and move right one
# character.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_LABEL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "This message box label caret movement to 'h'",
    ["BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=2",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'h'"]))

########################################################################
# Select the rest of the word "This".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(WaitAction("object:text-selection-changed",
                           None,
                           None,
                           pyatspi.ROLE_LABEL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "This message box label caret select 'his' of 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=5",
     "SPEECH OUTPUT: 'his'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "This message box label caret selection Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=5",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times:'",
     "SPEECH OUTPUT: 'selected label'"]))

########################################################################
# Do an extended "Where Am I" via double KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "This message box label caret selection Extended Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=5",
     "BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=5",
     "SPEECH OUTPUT: 'This message box has been popped up the following",
     "number of times:'",
     "SPEECH OUTPUT: 'selected label'"]))

########################################################################
# Arrow left to clear the selection and then do a Shift+Control+Left to
# select the beginning of the word "This".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left", 500))
sequence.append(KeyComboAction("<Shift><Control>Left", 500))
sequence.append(WaitAction("object:text-selection-changed",
                           None,
                           None,
                           pyatspi.ROLE_LABEL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "This message box label caret select 'T' in 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=2",
     "BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=1",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'T' voice=uppercase",
     "SPEECH OUTPUT: 'selected' voice=system"]))

########################################################################
# Reselect the rest of the word "This".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(WaitAction("object:text-selection-changed",
                           None,
                           None,
                           pyatspi.ROLE_LABEL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "This message box label caret select rest of 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Information Alert This message box has  $l'",
     "     VISIBLE:  'This message box has  $l', cursor=5",
     "SPEECH OUTPUT: 'This'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

########################################################################
# Close the demo subwindow.
#
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_LABEL))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Close the Dialogs demo window
#
#sequence.append(WaitForWindowActivate("Dialogs",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_PUSH_BUTTON))
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
