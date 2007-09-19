#!/usr/bin/python

"""Test of label presentation using the gtk-demo
   Dialog and Message Boxes demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

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
# Tab to the "This message box..." label.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Information Alert This message box has been popped up the following
# number of times: Label'
#      VISIBLE:  'This message box has been popped', cursor=1
#      
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'This message box has been popped up the following
# number of times: label'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_LABEL))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: the label text is selected, should it be marked
# as such in braille?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Information Alert This message box has been popped up the following
# number of times: Label'
#      VISIBLE:  'This message box has been popped', cursor=1
#
# SPEECH OUTPUT: 'This message box has been popped up the following
# number of times:'
# SPEECH OUTPUT: 'label'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Do an extended "Where Am I" via double KP_Enter.  The following should
# be presented [[[BUG?: the label text is selected -- should it be
# presented?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Information Alert This message box has been popped up the following
# number of times: Label'
#      VISIBLE:  'This message box has been popped', cursor=1
#
# SPEECH OUTPUT: 'This message box has been popped up the following
# number of times:'
# SPEECH OUTPUT: 'label'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Position the caret at the beginning of the label and move right one
# character.  The following should be presented [[[BUG?: the caret
# position in braille doesn't update.  This becomes worse as you scroll
# to text that is off the braille display -- the display doesn't scroll
# to show the text.  This cursor offset bug is prevalent throughout this
# test.]]]
#
# BRAILLE LINE:  'gtk-demo Application Information Alert This message box has been popped up the following
# number of times: Label'
#      VISIBLE:  'This message box has been popped', cursor=1
#
# SPEECH OUTPUT: 'h'
#
sequence.append(KeyComboAction("Home"))
sequence.append(KeyComboAction("Right", 500))

########################################################################
# Select the rest of the word "This".  [[[BUG?: we should be presenting
# the new selection, but we're not.]]]
#
sequence.append(KeyComboAction("<Shift><Control>Right", 500))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: the label text is selected, should it be marked
# as such in braille?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Information Alert This message box has been popped up the following
# number of times: Label'
#      VISIBLE:  'This message box has been popped', cursor=1
# SPEECH OUTPUT: 'This message box has been popped up the following
# number of times:'
# SPEECH OUTPUT: 'label'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Do an extended "Where Am I" via double KP_Enter.  The following should
# be presented [[[BUG?: the label text is selected -- should it be
# presented?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Information Alert This message box has been popped up the following
# number of times: Label'
#      VISIBLE:  'This message box has been popped', cursor=1
# SPEECH OUTPUT: 'This message box has been popped up the following
# number of times:'
# SPEECH OUTPUT: 'label'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Arrow left to clear the selection and then do a Shift+Control+Left to
# select the beginning of the word "This".  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Information Alert This message box has been popped up the following
# number of times: Label'
#      VISIBLE:  'This message box has been popped', cursor=1
#      
# SPEECH OUTPUT: 'T'
# SPEECH OUTPUT: 'selected'
#
sequence.append(KeyComboAction("Left", 500))
sequence.append(KeyComboAction("<Shift><Control>Left", 500))

########################################################################
# Reselect the rest of the word "This".  [[[BUG?: we should be presenting
# the new selection, but we're not.]]]
#
sequence.append(KeyComboAction("<Shift><Control>Right", 500))

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
