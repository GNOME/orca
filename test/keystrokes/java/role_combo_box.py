#!/usr/bin/python

"""Test of combo boxes in Java's SwingSet2."""

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
# Tab over to the combo box demo, and activate it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
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
sequence.append(WaitForFocus("ComboBox Demo", acc_role=pyatspi.ROLE_PAGE_TAB))

sequence.append(PauseAction(5000))

##########################################################################
# Focusing over first combo box
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Philip, Howard, Jeff", 
                             acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "1. focusing over first combo box",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Philip, Howard, Jeff Combo'",
     "     VISIBLE:  'Presets: Philip, Howard, Jeff Co', cursor=10",
     "SPEECH OUTPUT: 'ComboBox Demo page Presets: Philip, Howard, Jeff combo box'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Philip, Howard, Jeff Combo'",
     "     VISIBLE:  'Presets: Philip, Howard, Jeff Co', cursor=10",
     "SPEECH OUTPUT: 'Presets: combo box Philip, Howard, Jeff 1 of 10'"]))

##########################################################################
# Bring up combo box list by pressing space
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "3. Expand combo box",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Philip, Howard, Jeff Combo'",
     "     VISIBLE:  'Presets: Philip, Howard, Jeff Co', cursor=10",
     "SPEECH OUTPUT: 'Philip, Howard, Jeff'"]))
##########################################################################
# Arrow down to next list item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Jeff, Larry, Philip", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "4. Arrow Down",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Jeff, Larry, Philip Combo'",
     "     VISIBLE:  'Presets: Jeff, Larry, Philip Com', cursor=10",
     "SPEECH OUTPUT: 'Jeff, Larry, Philip'"]))

##########################################################################
# Arrow down to next list item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Howard, Scott, Hans", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "5. Arrow Down",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Howard, Scott, Hans Combo'",
     "     VISIBLE:  'Presets: Howard, Scott, Hans Com', cursor=10",
     "SPEECH OUTPUT: 'Howard, Scott, Hans'"]))

########################################################################
# [[[BUG 483212: Missing significant information when performing where am i on combo box items]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Howard, Scott, Hans'
# SPEECH OUTPUT: 'label'
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "6. basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Howard, Scott, Hans Combo'",
     "     VISIBLE:  'Presets: Howard, Scott, Hans Com', cursor=10",
     "SPEECH OUTPUT: 'Presets: combo box Howard, Scott, Hans 3 of 8'"]))

##########################################################################
# Arrow down to next list item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Philip, Jeff, Hans", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "7. Arrow Down",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Philip, Jeff, Hans Combo'",
     "     VISIBLE:  'Presets: Philip, Jeff, Hans Comb', cursor=10",
     "SPEECH OUTPUT: 'Philip, Jeff, Hans'"]))

##########################################################################
# Press return to close list and select current item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "8. Collapse combo box",
    ["KNOWN ISSUE - Orca often doesn't speak when Return is used to collapse a combo box; this is not limited to Java."]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "9. basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Philip, Jeff, Hans Combo'",
     "     VISIBLE:  'Presets: Philip, Jeff, Hans Comb', cursor=10",
     "SPEECH OUTPUT: 'Presets: combo box Philip, Jeff, Hans 4 of 8'"]))

##########################################################################
# Bring up combo box list by pressing space, the following should be 
# in output:
# 
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "10. Expand combo box",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Philip, Jeff, Hans Combo'",
     "     VISIBLE:  'Presets: Philip, Jeff, Hans Comb', cursor=10",
     "SPEECH OUTPUT: 'Philip, Jeff, Hans'"]))

##########################################################################
# Arrow up to previous list item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Howard, Scott, Hans", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "11. Arrow Up",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Howard, Scott, Hans Combo'",
     "     VISIBLE:  'Presets: Howard, Scott, Hans Com', cursor=10",
     "SPEECH OUTPUT: 'Howard, Scott, Hans'"]))

##########################################################################
# Arrow up to previous list item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Jeff, Larry, Philip", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "12. Arrow Up",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Jeff, Larry, Philip Combo'",
     "     VISIBLE:  'Presets: Jeff, Larry, Philip Com', cursor=10",
     "SPEECH OUTPUT: 'Jeff, Larry, Philip'"]))

##########################################################################
# Arrow up to previous list item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Philip, Howard, Jeff", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "13. Arrow Up",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Presets: Philip, Howard, Jeff Combo'",
     "     VISIBLE:  'Presets: Philip, Howard, Jeff Co', cursor=10",
     "SPEECH OUTPUT: 'Philip, Howard, Jeff'"]))

##########################################################################
# Press return to close list and select current item.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "14. Collapse combo box",
    ["KNOWN ISSUE - Orca often doesn't speak when Return is used to collapse a combo box; this is not limited to Java."]))

##########################################################################
# Tab to next combo box.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Philip", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "15. Tab to next combo box",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Hair: Philip Combo'",
     "     VISIBLE:  'Hair: Philip Combo', cursor=7",
     "SPEECH OUTPUT: 'Hair: Philip combo box'"]))

##########################################################################
# Tab to next combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Howard", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "16. Tab to next combo box",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Eyes & Nose: Howard Combo'",
     "     VISIBLE:  'Eyes & Nose: Howard Combo', cursor=14",
     "SPEECH OUTPUT: 'Eyes & Nose: Howard combo box'"]))

##########################################################################
# Tab to next combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Jeff", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "17. Tab to next combo box",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Page Mouth: Jeff Combo'",
     "     VISIBLE:  'Mouth: Jeff Combo', cursor=8",
     "SPEECH OUTPUT: 'Mouth: Jeff combo box'"]))

##########################################################################
# Tab back up to starting state
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
# Toggle the top left button, to return to normal state.
sequence.append(TypeAction           (" "))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
