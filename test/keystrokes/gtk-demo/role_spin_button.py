#!/usr/bin/python

"""Test of spin button output using the gtk-demo Color Selector demo
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Color Selector
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Color Selector", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Printing demo window appears, open the color selector.
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("Change the above color",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return", 500))

########################################################################
#
# When the "Changing color" window appears, tab to the "Hue" spin
# button.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_UNKNOWN))
sequence.append(KeyComboAction("Tab", 500))
sequence.append(KeyComboAction("Tab", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SPIN_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Hue spin button",
    ["KNOWN ISSUE - Selection state not spoken",
     "BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=6",
     "BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=9",
     "SPEECH OUTPUT: 'Hue: 240 spin button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Hue spin button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=9",
     "SPEECH OUTPUT: 'Hue: spin button 240 selected.'",
     "SPEECH OUTPUT: 'Alt h'",
     "SPEECH OUTPUT: 'Position on the color wheel.'"]))

########################################################################
# Change the value by arrowing down.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SPIN_BUTTON,
                           5000))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Hue spin button decrement value",
    ["BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=9",
     "BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=6",
     "BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 239 $l'",
     "     VISIBLE:  'Hue: 239 $l', cursor=6",
     "SPEECH OUTPUT: '240'",
     "SPEECH OUTPUT: '239'"]))

########################################################################
# Change the value by arrowing back up.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up", 500))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SPIN_BUTTON,
                           5000))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Hue spin button increment value",
    ["BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 239 $l'",
     "     VISIBLE:  'Hue: 239 $l', cursor=6",
     "BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=6",
     "SPEECH OUTPUT: '240'"]))

########################################################################
# Arrow right to move the caret.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_SPIN_BUTTON,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Hue spin button caret navigation",
    ["BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=7",
     "SPEECH OUTPUT: '4'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Hue spin button caret navigation",
    ["BRAILLE LINE:  'gtk-demo Application Changing color ColorChooser ColorChooser Hue: 240 $l'",
     "     VISIBLE:  'Hue: 240 $l', cursor=7",
     "SPEECH OUTPUT: 'Hue: spin button 240.'",
     "SPEECH OUTPUT: 'Alt h'",
     "SPEECH OUTPUT: 'Position on the color wheel.'"]))

########################################################################
# Close the Color Chooser dialog
#
sequence.append(KeyComboAction         ("<Alt>c"))

########################################################################
# Close the Color Chooser demo
#
sequence.append(WaitForFocus("Change the above color",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
