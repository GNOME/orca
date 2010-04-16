#!/usr/bin/python

"""Test of checkbox output using the gtk-demo Paned Widgets demo.
"""

from macaroon.playback import *

sequence = MacroSequence()
import utils

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

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

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "Left resize check box unchecked plus panel context",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel < > Resize CheckBox'",
     "     VISIBLE:  '< > Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Horizontal panel Resize check box not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Left resize check box unchecked Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel < > Resize CheckBox'",
     "     VISIBLE:  '< > Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Horizontal Resize check box not checked.'",
     "SPEECH OUTPUT: 'Alt r'"]))

########################################################################
# Now, change its state.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Left resize check box checked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel <x> Resize CheckBox'",
     "     VISIBLE:  '<x> Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Left resize check box checked Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel <x> Resize CheckBox'",
     "     VISIBLE:  '<x> Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Horizontal Resize check box checked.'",
     "SPEECH OUTPUT: 'Alt r'"]))

########################################################################
# Change the state back and move on to a few more check boxes.  The
# presentation in speech and braille should be similar to the above.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Left resize check box unchecked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel < > Resize CheckBox'",
     "     VISIBLE:  '< > Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "Right resize check box checked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel <x> Resize CheckBox'",
     "     VISIBLE:  '<x> Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Resize check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right resize check box unchecked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel < > Resize CheckBox'",
     "     VISIBLE:  '< > Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right resize check box checked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Horizontal Panel <x> Resize CheckBox'",
     "     VISIBLE:  '<x> Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "Top resize check box checked plus panel context",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Vertical Panel < > Resize CheckBox'",
     "     VISIBLE:  '< > Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Vertical panel Resize check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Top resize check box unchecked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Vertical Panel <x> Resize CheckBox'",
     "     VISIBLE:  '<x> Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Top resize check box checked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Vertical Panel < > Resize CheckBox'",
     "     VISIBLE:  '< > Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Resize", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "Bottom resize check box checked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Vertical Panel <x> Resize CheckBox'",
     "     VISIBLE:  '<x> Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Resize check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Bottom resize check box unchecked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Vertical Panel < > Resize CheckBox'",
     "     VISIBLE:  '< > Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Bottom resize check box unchecked",
    ["BRAILLE LINE:  'gtk-demo Application Panes Frame Vertical Panel <x> Resize CheckBox'",
     "     VISIBLE:  '<x> Resize CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

########################################################################
# Close the Panes demo window
#
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
