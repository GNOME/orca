# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of menu accelerator label output of Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# [[[BUG: Sometimes menus on the menu bar in Firefox are claiming to be
# menu items. See https://bugzilla.mozilla.org/show_bug.cgi?id=396799]]]
#

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "File" menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(utils.AssertPresentationAction(
    "File menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Application MenuBar New Tab\(Control T\)'",
     "     VISIBLE:  'New Tab(Control T)', cursor=1",
     "SPEECH OUTPUT: 'File menu New Tab Control T'"]))

########################################################################
# Now, continue on down the menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in File menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Application MenuBar New Window\(Control N\)'",
     "     VISIBLE:  'New Window\(Control N\)', cursor=1",
     "SPEECH OUTPUT: 'New Window Control N'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in File menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Application MenuBar Open Location...\(Control L\)'",
     "     VISIBLE:  'Open Location...(Control L)', cursor=1",
     "SPEECH OUTPUT: 'Open Location… Control L'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in File menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Application MenuBar Open File...\(Control O\)'",
     "     VISIBLE:  'Open File...(Control O)', cursor=1",
     "SPEECH OUTPUT: 'Open File… Control O'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Application MenuBar Open File...\(Control O\)'",
     "     VISIBLE:  'Open File...(Control O)', cursor=1",
     "SPEECH OUTPUT: 'tool bar File menu Open File… Control O 4 of [0-9]+.'",
     "SPEECH OUTPUT: 'O'"]))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
