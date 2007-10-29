#!/usr/bin/python

"""Test of radio button output using the gtk-demo Printing demo
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
# Once gtk-demo is running, invoke the Printing demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Printing", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Printing demo window appears, navigate to the "All" radio
# button.
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("General", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>a", 500))
sequence.append(WaitForFocus("All", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "All radio button",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Print Pages Filler &=y All RadioButton'",
     "     VISIBLE:  '&=y All RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Print Pages'",
     "SPEECH OUTPUT: 'All selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "All radio button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Print Pages Filler &=y All RadioButton'",
     "     VISIBLE:  '&=y All RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Print Pages'",
     "SPEECH OUTPUT: 'All radio button'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'item 1 of 3'",
     "SPEECH OUTPUT: ' Alt a'"]))

########################################################################
# Down arrow to the "Range" radio button.
# 
# presented [[[BUG?: when you first arrow to a radio button, we present
# it as not selected in the tests, but manual testing presents it as
# selected.  It should be presented as selected.  Something's wrong,
# but I suspect we're getting a focus event before the state change
# event.  Because our normal operating mode of Orca is asynchronous,
# it's likely that the state has already changed by the time we handle
# the focus event.]]]:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Range", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Range radio button",
    ["BUG? - the radio button should be presented as selected.",
     "BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Print Pages Filler & y Range RadioButton'",
     "     VISIBLE:  '& y Range RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Range not selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Range radio button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Print Pages Filler &=y Range RadioButton'",
     "     VISIBLE:  '&=y Range RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Print Pages'",
     "SPEECH OUTPUT: 'Range radio button'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'item 3 of 3'",
     "SPEECH OUTPUT: ' Alt n'"]))

########################################################################
# Put everything back and close the demo.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("All", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "All radio button",
    ["BUG? - the radio button should be presented as selected.",
     "BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Print Pages Filler & y All RadioButton'",
     "     VISIBLE:  '& y All RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'All not selected radio button'"]))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
sequence.append(KeyComboAction("<Alt>c", 500))
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
