#!/usr/bin/python

"""Test of menu accelerator label output of Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# NOTE: Sometimes menus on the menu bar in Firefox are claiming to be
# menu items. See https://bugzilla.mozilla.org/show_bug.cgi?id=396799
#

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu.
#
sequence.append(KeyComboAction("<Alt>f"))

########################################################################
# When the "New Window" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar New Window(Control N)'
#      VISIBLE:  'New Window(Control N)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'New Window Control N'
#
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "New Tab" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar New Tab(Control T)'
#      VISIBLE:  'New Tab(Control T)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'New Tab Control T'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("New Tab", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Open Location..." menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Open Location...(Control L)'
#      VISIBLE:  'Open Location...(Control L)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Open Location... Control L'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Open Location...", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Open File..." menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Open File...(Control O)'
#      VISIBLE:  'Open File...(Control O)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Open File... Control O'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Open File...", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Close" menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Close(Control W)'
#      VISIBLE:  'Close(Control W)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Close Control W'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Close", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Save Page As..." menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Save Page As...(Control S)'
#      VISIBLE:  'Save Page As...(Control S)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Save Page As... Control S'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Save Page As...", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now, continue on down the menu.
#
# When the "Send Link..." menu item gets focus, the following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Send Link...'
#      VISIBLE:  'Send Link...', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Send Link...'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Send Link...", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Send Link...'
#      VISIBLE:  'Send Link...', cursor=1
# SPEECH OUTPUT: 'File menu'
# SPEECH OUTPUT: 'Send Link...'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 7 of 13'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
