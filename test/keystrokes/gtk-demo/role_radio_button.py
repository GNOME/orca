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

########################################################################
# Once gtk-demo is running, invoke the Printing demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Printing", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Printing demo window appears, navigate to the "All Pages" radio
# button.
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("General", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>a", 500))
sequence.append(WaitForFocus("All Pages", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "All Pages radio button",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Page Range &=y All Pages RadioButton'",
     "     VISIBLE:  '&=y All Pages RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Range All Pages selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "All Pages radio button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Page Range &=y All Pages RadioButton'",
     "     VISIBLE:  '&=y All Pages RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Range All Pages radio button selected 1 of 3.'",
     "SPEECH OUTPUT: 'Alt a'"]))

# WDW - the printing dialog changed for 2.27.x - the pages radio button
# takes you to the text entry field now.  We'll comment this out for now.
#
#########################################################################
## Down arrow to the "Pages:" radio button.
## 
## presented [[[BUG?: when you first arrow to a radio button, we present
## it as not selected in the tests, but manual testing presents it as
## selected.  It should be presented as selected.  Something's wrong,
## but I suspect we're getting a focus event before the state change
## event.  Because our normal operating mode of Orca is asynchronous,
## it's likely that the state has already changed by the time we handle
## the focus event.]]]:
##
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(WaitForFocus("Pages:", acc_role=pyatspi.ROLE_RADIO_BUTTON))
#sequence.append(utils.AssertPresentationAction(
#    "Range radio button",
#    ["KNOWN ISSUE - the radio button should be presented as selected.",
#     "BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Page Range & y Pages: RadioButton'",
#     "     VISIBLE:  '& y Pages: RadioButton', cursor=1",
#     "SPEECH OUTPUT: 'Pages: not selected radio button'"]))
#
#########################################################################
## Do a basic "Where Am I" via KP_Enter.
##
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("KP_Enter"))
#sequence.append(PauseAction(3000))
#sequence.append(utils.AssertPresentationAction(
#    "Range radio button Where Am I",
#    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Page Range &=y Pages: RadioButton'",
#     "     VISIBLE:  '&=y Pages: RadioButton', cursor=1",
#     "SPEECH OUTPUT: 'Range Pages: radio button selected 3 of 3.'",
#     "SPEECH OUTPUT: 'Alt e'"]))
#
#########################################################################
## Put everything back and close the demo.
##
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Up"))
#sequence.append(WaitForFocus("All Pages", acc_role=pyatspi.ROLE_RADIO_BUTTON))
#sequence.append(utils.AssertPresentationAction(
#    "All Pages radio button",
#    ["KNOWN ISSUE - the radio button should be presented as selected.",
#     "BRAILLE LINE:  'gtk-demo Application Print Dialog TabList General Page Range & y All Pages RadioButton'",
#     "     VISIBLE:  '& y All Pages RadioButton', cursor=1",
#     "SPEECH OUTPUT: 'All Pages not selected radio button'"]))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
sequence.append(KeyComboAction("<Alt>c", 500))
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
