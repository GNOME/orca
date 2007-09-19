#!/usr/bin/python

"""Test of radio menu item output using the gtk-demo
   Application Main Window demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, open the Preferences menu and right arrow to
# the "Red" menu item under the "Color" sub menu.  The following
# should be presented when the "Red" menu item gets focus [[[BUG?: these
# show up as check menu items in AT-SPI, but they are visually represented
# as radio menu items.  Does GAIL have a bug with radio menu items?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu <x> Red CheckItem(Control r)'
#      VISIBLE:  '<x> Red CheckItem(Control r)', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Red check item checked Control r'
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Red", acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu <x> Red CheckItem(Control r)'
#      VISIBLE:  '<x> Red CheckItem(Control r)', cursor=1
#
# SPEECH OUTPUT: 'Color menu'
# SPEECH OUTPUT: 'Red'
# SPEECH OUTPUT: 'check item'
# SPEECH OUTPUT: 'checked'
# SPEECH OUTPUT: 'Control r'
# SPEECH OUTPUT: 'item 1 of 3'
# SPEECH OUTPUT: 'r'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Down arrow to the "Green" menu item.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu < > Green CheckItem(Control g)'
#      VISIBLE:  '< > Green CheckItem(Control g)', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Green check item not checked Control g'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Green",
                             acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame MenuBar Preferences Menu < > Green CheckItem(Control g)'
#      VISIBLE:  '< > Green CheckItem(Control g)', cursor=1
#
# SPEECH OUTPUT: 'Color menu'
# SPEECH OUTPUT: 'Green'
# SPEECH OUTPUT: 'check item'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: 'Control g'
# SPEECH OUTPUT: 'item 2 of 3'
# SPEECH OUTPUT: 'g'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
