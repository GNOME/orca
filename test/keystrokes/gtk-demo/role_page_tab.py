#!/usr/bin/python

"""Test of page tab output using the gtk-demo Printing demo
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
sequence.append(TypeAction("Printing"))
sequence.append(KeyComboAction("Return", 500))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 500))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "General page tab",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog'",
     "     VISIBLE:  'Print Dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Print Dialog TabList'",
     "     VISIBLE:  'TabList', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Print Dialog General Page'",
     "     VISIBLE:  'General Page', cursor=1",
     "SPEECH OUTPUT: 'Print Range Copies'",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'General page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "General page tab Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog General Page'",
     "     VISIBLE:  'General Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'General'",
     "SPEECH OUTPUT: 'page 1 of 2'"]))

########################################################################
# Arrow Right to the "Page Setup" tab.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Page Setup", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "Page Setup page tab",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog Page Setup Page'",
     "     VISIBLE:  'Page Setup Page', cursor=1",
     "SPEECH OUTPUT: 'Page Setup page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Page Setup page tab Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog Page Setup Page'",
     "     VISIBLE:  'Page Setup Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Page Setup'",
     "SPEECH OUTPUT: 'page 2 of 2'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction         ("<Alt>c"))

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
