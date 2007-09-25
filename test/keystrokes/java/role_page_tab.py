#!/usr/bin/python

"""Test of page tabs in Java's SwingSet2.
"""

from macaroon.playback.keypress_mimic import *

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
sequence.append(KeyComboAction("Tab"))

########################################################################
# Expected output when "Laine" tab gets focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Laine'
#      VISIBLE:  'Laine', cursor=1
#
# SPEECH OUTPUT: 'Laine tab list'
# SPEECH OUTPUT: 'Laine page'
sequence.append(WaitForFocus("Laine", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))

########################################################################
# Expected output when "Ewan" tab gets focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Ewan'
#      VISIBLE:  'Ewan', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Ewan page'
sequence.append(WaitForFocus("Ewan", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))

########################################################################
# Expected output when "Hania" tab gets focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo Hania'
#      VISIBLE:  'Hania', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Hania page'
sequence.append(WaitForFocus("Hania", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))

########################################################################
# Expected output when "Bouncing Babies!" tab gets focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane TabbedPane Demo TabList TabbedPane Demo <html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html>'
#      VISIBLE:  '<html><font color=blue><bold><ce', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: '<html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html> page'
sequence.append(WaitForFocus("<html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html>", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: '<html><font color=blue><bold><center>Bouncing Babies!</center></bold></font></html> page'
# SPEECH OUTPUT: 'item 4 of 4'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Hania", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: 'Hania page'
# SPEECH OUTPUT: 'item 3 of 4'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Ewan", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: 'Ewan page'
# SPEECH OUTPUT: 'item 2 of 4'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Laine", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: 'Laine page'
# SPEECH OUTPUT: 'item 1 of 4'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

# Toggle the top left button, to return to normal state.
sequence.append(TypeAction           (" "))

sequence.append(PauseAction(3000))

sequence.start()
