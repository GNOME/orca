#!/usr/bin/python

"""Test of push buttons in Java's SwingSet2."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

# Wait for entire window to get populated.
sequence.append(PauseAction(5000))

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
sequence.append(WaitForFocus("Buttons", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(PauseAction(5000))

##########################################################################
# Expected output when focusing over first button.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("One ", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "1. Move to One button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Buttons TabList Buttons Page Text Buttons Panel One  Button'",
     "     VISIBLE:  'One  Button', cursor=1",
     "SPEECH OUTPUT: 'Text Buttons panel One  button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Buttons TabList Buttons Page Text Buttons Panel One  Button'",
     "     VISIBLE:  'One  Button', cursor=1",
     "SPEECH OUTPUT: 'One  button'"]))

##########################################################################
# Expected output when focusing over second button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "3. Move to Two button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Buttons TabList Buttons Page Text Buttons Panel Two Button'",
     "     VISIBLE:  'Two Button', cursor=1",
     "SPEECH OUTPUT: 'Two button'"]))

##########################################################################
# Expected output when focusing over third button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("<html><font size=2 color=red><bold>Three!</font></html>", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "4. Move to Three button",
    ["BUG? - What's up with the extra whitespace in the speech?",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Buttons TabList Buttons Page Text Buttons Panel Three! Button'",
     "     VISIBLE:  'Three! Button', cursor=1",
     "SPEECH OUTPUT: '",
"Three! button'"]))

##########################################################################
# Image buttons
##########################################################################
# Expected output when focusing over first image button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "5. Move to first image button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Buttons TabList Buttons Page Image Buttons Panel Button'",
     "     VISIBLE:  'Button', cursor=1",
     "SPEECH OUTPUT: 'Image Buttons panel button'"]))

##########################################################################
# Expected output when focusing over second image button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "6. Move to second image button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Buttons TabList Buttons Page Image Buttons Panel Button'",
     "     VISIBLE:  'Button', cursor=1",
     "SPEECH OUTPUT: 'button'"]))

##########################################################################
# Expected output when focusing over third image button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "7. Move to third image button",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Button Demo TabList Button Demo Page Buttons TabList Buttons Page Image Buttons Panel Button'",
     "     VISIBLE:  'Button', cursor=1",
     "SPEECH OUTPUT: 'button'"]))

##########################################################################
# Wrap around tabbing to top left toggle button.
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
sequence.append(TypeAction           (" "))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
