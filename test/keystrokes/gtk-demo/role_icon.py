#!/usr/bin/python

"""Test of icon output using the gtk-demo Icon View Basics demo under
   the Icon View area.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Icon View Basics demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View Basics", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the GtkIconView demo is up, the following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane'
#      VISIBLE:  'LayeredPane', cursor=1
#
# SPEECH OUTPUT: 'GtkIconView demo frame'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'layered pane'
#
#sequence.append(WaitForWindowActivate("GtkIconView demo",None))
# ""
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_LAYERED_PANE))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane'
#      VISIBLE:  'LayeredPane', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'layered pane'
#
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Down into the icon list, finally making something be selected in the
# view.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane bin Icon'
#      VISIBLE:  'bin Icon', cursor=1
#     
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'bin icon'
#
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: the bin icon is shown as selected in the view,
# so should it be "1 of n items selected"?]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane bin Icon'
#      VISIBLE:  'bin Icon', cursor=1
#
# SPEECH OUTPUT: 'Icon panel'
# SPEECH OUTPUT: 'bin'
# SPEECH OUTPUT: 'icon'
# SPEECH OUTPUT: '0 of 26 items selected'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Arrow right and wait for the next icon to be selected.  The
# presentation should be similar to the following:
#
# BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane boot Icon'
#      VISIBLE:  'boot Icon', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'boot icon'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))

########################################################################
# Select more than one icon by doing Shift+Right.  [[[BUG?: should
# Orca announce "selected" when an icon is selected?]]]
#
sequence.append(KeyComboAction("<Shift>Right", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: should it be "2 of n items selected"?]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane cdrom Icon'
#      VISIBLE:  'cdrom Icon', cursor=1
#
# SPEECH OUTPUT: 'Icon panel'
# SPEECH OUTPUT: 'cdrom'
# SPEECH OUTPUT: 'icon'
# SPEECH OUTPUT: '0 of 26 items selected'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Close the GtkIconView demo window
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("<Control>f"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
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
