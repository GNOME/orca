#!/usr/bin/python

"""Test of check boxes in Java's SwingSet2.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

# Wait for entire window to get populated.
sequence.append(PauseAction(10000))

##########################################################################
# Tab over to the button demo, and activate it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(TypeAction(" "))

##########################################################################
# Tab all the way down to the button page tab.
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
sequence.append(WaitForFocus("Button Demo", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Tab"))

##########################################################################
# Select Check Boxes tab
#
sequence.append(WaitForFocus("Buttons", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Radio Buttons", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Check Boxes", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(PauseAction(5000))

##########################################################################
# Tab into check boxes container
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("One ", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "One checkbox unchecked",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Text CheckBoxes Panel < > One  CheckBox'",
     "     VISIBLE:  '< > One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Text CheckBoxes panel One  check box not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "One checkbox unchecked Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Text CheckBoxes Panel < > One  CheckBox'",
     "     VISIBLE:  '< > One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Text CheckBoxes One  check box not checked'"]))

########################################################################
# Now, change its state.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX,5000))
sequence.append(utils.AssertPresentationAction(
    "One checkbox checked",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Text CheckBoxes Panel <x> One  CheckBox'",
     "     VISIBLE:  '<x> One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "One checked Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Text CheckBoxes Panel <x> One  CheckBox'",
     "     VISIBLE:  '<x> One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Text CheckBoxes One  check box checked'"]))

########################################################################
# Change the state back and move on to a few more check boxes.  The
# presentation in speech and braille should be similar to the above.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))
sequence.append(utils.AssertPresentationAction(
    "One checkbox unchecked",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Text CheckBoxes Panel < > One  CheckBox'",
     "     VISIBLE:  '< > One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Three", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Tab to the One lightbulb
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("One ", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(utils.AssertPresentationAction(
    "One lightbulb checkbox unchecked",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Image CheckBoxes Panel < > One  CheckBox'",
     "     VISIBLE:  '< > One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Image CheckBoxes panel One  check box not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "One lightbulb unchecked checkbox Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Image CheckBoxes Panel < > One  CheckBox'",
     "     VISIBLE:  '< > One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Image CheckBoxes One  check box not checked'"]))

########################################################################
# Change the state back and move on to a few more check boxes.  The
# presentation in speech and braille should be similar to the above.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))
sequence.append(utils.AssertPresentationAction(
    "One lightbulb checkbox checked",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Image CheckBoxes Panel <x> One  CheckBox'",
     "     VISIBLE:  '<x> One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(' '))
sequence.append(WaitAction("object:state-changed:checked", None,
                           None, pyatspi.ROLE_CHECK_BOX, 5000))
sequence.append(utils.AssertPresentationAction(
    "One lightbulb unchecked checkbox",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Check Boxes TabList Check Boxes Page Image CheckBoxes Panel < > One  CheckBox'",
     "     VISIBLE:  '< > One  CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Three", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Paint Border", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Paint Focus", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Enabled", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Content Filled", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Default", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("0", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("10", acc_role=pyatspi.ROLE_RADIO_BUTTON))
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
