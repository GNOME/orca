#!/usr/bin/python

"""Test of page tabs in Java's SwingSet2."""

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
# Tab over to the JTabbedPane demo, and activate it.
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
sequence.append(TypeAction(" "))
##########################################################################
# Tab all the way down to the demo.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("TabbedPane Demo", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Top", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Left", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Bottom", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Right", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Expected output when "Laine" tab gets focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Laine", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "1. Move to Laine tab",
    ["BUG? - Seems extra chatty",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Laine Page'",
     "     VISIBLE:  'Laine Page', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Laine TabList'",
     "     VISIBLE:  'Laine TabList', cursor=1",
     "SPEECH OUTPUT: 'Laine tab list Laine page'",
     "SPEECH OUTPUT: 'Laine tab list'"]))

########################################################################
# Expected output when "Ewan" tab gets focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Ewan", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "2. Move to Ewan tab",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Ewan Page'",
     "     VISIBLE:  'Ewan Page', cursor=1",
     "SPEECH OUTPUT: 'Ewan page'"]))

########################################################################
# Expected output when "Hania" tab gets focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Hania", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "3. Move to Hania tab",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Hania Page'",
     "     VISIBLE:  'Hania Page', cursor=1",
     "SPEECH OUTPUT: 'Hania page'"]))

########################################################################
# Expected output when "Bouncing Babies!" tab gets focus.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("<html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html>", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "4. Move to Bouncing Babies! tab",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page <html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html> Page'",
     "     VISIBLE:  '<html><font color=blue><bold><ce', cursor=1",
     "SPEECH OUTPUT: '<html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html> page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "5. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page <html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html> Page'",
     "     VISIBLE:  '<html><font color=blue><bold><ce', cursor=1",
     "SPEECH OUTPUT: 'tab list <html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html> page 4 of 4'"]))
     
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Hania", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "6. Back to Hania tab",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Hania Page'",
     "     VISIBLE:  'Hania Page', cursor=1",
     "SPEECH OUTPUT: 'Hania page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "7. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Hania Page'",
     "     VISIBLE:  'Hania Page', cursor=1",
     "SPEECH OUTPUT: 'tab list Hania page 3 of 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Ewan", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "8. Back to Ewan tab",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Ewan Page'",
     "     VISIBLE:  'Ewan Page', cursor=1",
     "SPEECH OUTPUT: 'Ewan page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "9. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Ewan Page'",
     "     VISIBLE:  'Ewan Page', cursor=1",
     "SPEECH OUTPUT: 'tab list Ewan page 2 of 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Laine", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "10. Back to Laine tab",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Laine Page'",
     "     VISIBLE:  'Laine Page', cursor=1",
     "SPEECH OUTPUT: 'Laine page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "11. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Page Laine Page'",
     "     VISIBLE:  'Laine Page', cursor=1",
     "SPEECH OUTPUT: 'tab list Laine page 1 of 4'"]))

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
