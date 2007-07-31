#!/usr/bin/python

"""Test of icon output using the gtk-demo Icon View Basics demo under
   the Icon View area.
"""

from macaroon.playback.keypress_mimic import *

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
sequence.append(TypeAction("Icon View"))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View Basics"))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the GtkIconView demo is up, arrow around a few icons
#
#sequence.append(WaitForWindowActivate("GtkIconView demo",None))
# ""
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_LAYERED_PANE))
sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitForFocus("bin", acc_role=pyatspi.ROLE_ICON))
sequence.append(KeyComboAction("Right", 500))

sequence.append(WaitForFocus("boot", acc_role=pyatspi.ROLE_ICON))
sequence.append(KeyComboAction("Right", 500))

sequence.append(WaitForFocus("cdrom", acc_role=pyatspi.ROLE_ICON))

########################################################################
# Close the GtkIconView demo window
#
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("<Control>f"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View"))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

sequence.start()
