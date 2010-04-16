#!/usr/bin/python

"""Test of radio menu item output using the gtk-demo
   Application Main Window demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, open the Preferences menu and right arrow to
# the "Red" menu item under the "Color" sub menu.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Red", acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Red button",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu <x> Red CheckItem(Control r)'",
     "     VISIBLE:  '<x> Red CheckItem(Control r)', cursor=1",
     "SPEECH OUTPUT: 'Red check item checked Control r'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
# JD to WDW: I'm not sure if this is a regression or not. Now we are
# speaking a parent menu which we were not before. I *think* that's
# a bug fix. :-)
#
# WDW to JD: I agree -- it looks like a bug fix (yeah!)
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Red button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu <x> Red CheckItem(Control r)'",
     "     VISIBLE:  '<x> Red CheckItem(Control r)', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu Color menu Red check item checked Control r 1 of 3.",
     "SPEECH OUTPUT: 'r'"]))

########################################################################
# Down arrow to the "Green" menu item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Green",
                             acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Green button",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu < > Green CheckItem(Control g)'",
     "     VISIBLE:  '< > Green CheckItem(Control g)', cursor=1",
     "SPEECH OUTPUT: 'Green check item not checked Control g'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
# JD to WDW: I'm not sure if this is a regression or not. Now we are
# speaking a parent menu which we were not before. I *think* that's
# a bug fix. :-)
#
# WDW to JD: I agree -- it looks like a bug fix (yeah!)
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Green button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu < > Green CheckItem(Control g)'",
     "     VISIBLE:  '< > Green CheckItem(Control g)', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu Color menu Green check item not checked Control g 2 of 3.",
     "SPEECH OUTPUT: 'g'"]))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("F10"))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
