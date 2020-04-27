#!/usr/bin/python

"""Test of accelerator labels in Java's SwingSet2."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F10"))
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "1. F10 for File menu",
    ["KNOWN ISSUE - Sometimes more of the hierarchy is included in the braille; other times it is not. This applies to all tests here.",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "SPEECH OUTPUT: 'File menu'"]))
    
########################################################################
# Down Arrow to the About menu item
#
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("About", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "2. Arrow Down",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar About'",
     "     VISIBLE:  'About', cursor=1",
     "SPEECH OUTPUT: 'About'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar About'",
     "     VISIBLE:  'About', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Swing demo menu bar menu bar File menu About 1 of 5.'",
     "SPEECH OUTPUT: 'B'",
     "SPEECH OUTPUT: 'Find out about the SwingSet2 application'"]))

########################################################################
# Down Arrow to the Exit menu item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Exit", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "4. Arrow Down",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar Exit'",
     "     VISIBLE:  'Exit', cursor=1",
     "SPEECH OUTPUT: 'Exit'"]))

########################################################################
# Return SwingSet2 to beginning state.
sequence.append(KeyComboAction("Escape"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
