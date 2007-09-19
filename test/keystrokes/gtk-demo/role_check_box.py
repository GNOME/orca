#!/usr/bin/python

"""Test of checkbox output using the gtk-demo Paned Widgets demo.
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
# When the demo comes up, interact with a few check boxes
#
#sequence.append(WaitForWindowActivate("Panes",None))
sequence.append(WaitForFocus("Hi there", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

########################################################################
# When the "Resize" checkbox gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Horizontal Panel < > Resize CheckBox'
#      VISIBLE:  '< > Resize CheckBox', cursor=1
#
# SPEECH OUTPUT: 'Horizontal panel'
# SPEECH OUTPUT: 'Resize check box not checked'
#
sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Horizontal Panel < > Resize CheckBox'
#      VISIBLE:  '< > Resize CheckBox', cursor=1
# SPEECH OUTPUT: 'Resize check box'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: ' Alt r'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Now, change its state.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Horizontal Panel <x> Resize CheckBox'
#      VISIBLE:  '<x> Resize CheckBox', cursor=1
#
# SPEECH OUTPUT: 'checked'
#
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Horizontal Panel <x> Resize CheckBox'
#      VISIBLE:  '<x> Resize CheckBox', cursor=1
#
# SPEECH OUTPUT: 'Resize check box'
# SPEECH OUTPUT: 'checked'
# SPEECH OUTPUT: ' Alt r'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Change the state back and move on to a few more check boxes.  The
# presentation in speech and braille should be similar to the above.
#
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Shrink", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Shrink", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))

########################################################################
# Close the Panes demo window
#
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
