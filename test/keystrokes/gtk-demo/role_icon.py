#!/usr/bin/python

"""Test of icon output using the gtk-demo Icon View Basics demo under
   the Icon View area.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Icon View Basics demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Icon View Basics", 1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_LAYERED_PANE))
sequence.append(utils.AssertPresentationAction(
    "Layered pane focus",
    ["BRAILLE LINE:  'Window Icon View Basics $l'",
     "     VISIBLE:  'Window Icon View Basics $l', cursor=24",
     "BRAILLE LINE:  'Window Icon View Basics $l'",
     "     VISIBLE:  'Window Icon View Basics $l', cursor=8",
     "BRAILLE LINE:  'gtk-demo Application GTK+ Code Demos Frame TabList Widget (double click for demo) Page ScrollPane TreeTable Widget (double click for demo) ColumnHeader Icon View Basics TREE LEVEL 2'",
     "     VISIBLE:  'Icon View Basics TREE LEVEL 2', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame'",
     "     VISIBLE:  'GtkIconView demo Frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane'",
     "     VISIBLE:  'LayeredPane', cursor=1",
     "SPEECH OUTPUT: 'Widget (double click for demo) page Widget (double click for demo) column header Icon View Basics tree level 2'",
     "SPEECH OUTPUT: 'GtkIconView demo frame'",
     "SPEECH OUTPUT: 'layered pane'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Layered pane Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane'",
     "     VISIBLE:  'LayeredPane', cursor=1",
     "SPEECH OUTPUT: 'layered pane 0 of [0-9]+ items selected on 0 of [0-9]+'"]))

########################################################################
# Down into the icon list, finally making something be selected in the
# view.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))
sequence.append(utils.AssertPresentationAction(
    "bin icon",
    ["BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane bin Icon'",
     "     VISIBLE:  'bin Icon', cursor=1",
     "SPEECH OUTPUT: 'bin icon not selected'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "bin icon Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane bin Icon'",
     "     VISIBLE:  'bin Icon', cursor=1",
     "SPEECH OUTPUT: 'Icon panel bin [0-9] of [0-9]+ items selected on 1 of [0-9]+'"]))

########################################################################
# Arrow right and wait for the next icon to be selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))
sequence.append(utils.AssertPresentationAction(
    "boot icon",
    ["BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane boot Icon'",
     "     VISIBLE:  'boot Icon', cursor=1",
     "SPEECH OUTPUT: 'boot icon not selected'"]))

########################################################################
# Select more than one icon by doing Shift+Right.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Left", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ICON))
sequence.append(utils.AssertPresentationAction(
    "icon selection",
    ["BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane bin Icon'",
     "     VISIBLE:  'bin Icon', cursor=1",
     "SPEECH OUTPUT: 'bin icon not selected'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "icon selection Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkIconView demo Frame ScrollPane LayeredPane bin Icon'",
     "     VISIBLE:  'bin Icon', cursor=1",
     "SPEECH OUTPUT: 'Icon panel bin [0-9] of [0-9]+ items selected on 1 of [0-9]+'"]))

########################################################################
# Close the GtkIconView demo window
#
sequence.append(KeyComboAction("<Alt>F4", 1000))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))

sequence.append(TypeAction("Icon View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

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
