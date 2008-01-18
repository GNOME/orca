#!/usr/bin/python

"""Test of status bar output of Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local status bar test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "status-bar.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Status Bar Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Press a button to change the status bar text'",
     "     VISIBLE:  'Press a button to change the sta', cursor=1",
     "SPEECH OUTPUT: 'Press a button to change the status bar text'"]))

########################################################################
# Press Tab to the first push button and press it with space bar.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to button", 
    ["BRAILLE LINE:  'Who expects the Spanish Inquisition? Button'",
     "     VISIBLE:  'Who expects the Spanish Inquisit', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Who expects the Spanish Inquisition? button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "Press button", 
    [""]))

########################################################################
# Read the status bar with Orca+KP_ENTER double clicked.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Status bar", 
    ["BRAILLE LINE:  'Who expects the Spanish Inquisition? Button'",
     "     VISIBLE:  'Who expects the Spanish Inquisit', cursor=1",
     "BRAILLE LINE:  'Who expects the Spanish Inquisition? Button'",
     "     VISIBLE:  'Who expects the Spanish Inquisit', cursor=1",
     "SPEECH OUTPUT: 'Status Bar Regression Test - Minefield'",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition!'"]))

########################################################################
# Press Tab to the second push button and press it with space bar.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to button", 
    ["BRAILLE LINE:  'Our chief weapon is... Button'",
     "     VISIBLE:  'Our chief weapon is... Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Our chief weapon is... button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "Press button", 
    [""]))

########################################################################
# Read the status bar with Orca+KP_ENTER double clicked.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Status bar", 
    ["BRAILLE LINE:  'Our chief weapon is... Button'",
     "     VISIBLE:  'Our chief weapon is... Button', cursor=1",
     "BRAILLE LINE:  'Our chief weapon is... Button'",
     "     VISIBLE:  'Our chief weapon is... Button', cursor=1",
     "SPEECH OUTPUT: 'Status Bar Regression Test - Minefield'",
     "SPEECH OUTPUT: 'Surprise.  Surprise and fear. Fear and surprise... And ruthless efficiency...  And an almost fanatical devotion to the Pope... And nice red uniforms.'"]))

########################################################################
# Press Tab to the third push button and press it with space bar.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to button", 
    ["BRAILLE LINE:  'Fetch the COMFY CHAIR (AKA clear out the status bar) Button'",
     "     VISIBLE:  'Fetch the COMFY CHAIR (AKA clear', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Fetch the COMFY CHAIR (AKA clear out the status bar) button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "Press button", 
    [""]))

########################################################################
# Read the status bar with Orca+KP_ENTER double clicked.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Status bar", 
    ["BRAILLE LINE:  'Fetch the COMFY CHAIR (AKA clear out the status bar) Button'",
     "     VISIBLE:  'Fetch the COMFY CHAIR (AKA clear', cursor=1",
     "BRAILLE LINE:  'Fetch the COMFY CHAIR (AKA clear out the status bar) Button'",
     "     VISIBLE:  'Fetch the COMFY CHAIR (AKA clear', cursor=1",
     "SPEECH OUTPUT: 'Status Bar Regression Test - Minefield'",
     "SPEECH OUTPUT: 'Done'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
