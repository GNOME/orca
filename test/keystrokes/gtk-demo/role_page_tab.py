#!/usr/bin/python

"""Test of page tab output using the gtk-demo Printing demo
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Printing demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Printing", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Printing demo window appears, the following should be
# presented [[[BUG?: should the braille for the page tab rolename be
# presented in braille?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Print Dialog General'
#      VISIBLE:  'General', cursor=1
#
# SPEECH OUTPUT: 'Print Print Pages Copies'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'General page'
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("General", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Print Dialog General'
#      VISIBLE:  'General', cursor=1
#
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: 'General page'
# SPEECH OUTPUT: 'item 1 of 2'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Arrow Right to the "Page Setup" tab.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Print Dialog Page Setup'
#      VISIBLE:  'Page Setup', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Page Setup page'
# 
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Page Setup", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Print Dialog Page Setup'
#      VISIBLE:  'Page Setup', cursor=1
# 
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: 'Page Setup page'
# SPEECH OUTPUT: 'item 2 of 2'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction         ("<Alt>c"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
