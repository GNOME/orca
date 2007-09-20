#!/usr/bin/python

"""Test of menu radio button output using Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "View" menu.
#
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(WaitForFocus("Toolbars", acc_role=pyatspi.ROLE_MENU))

########################################################################
# When focus is on Toolbars, Press Y to open the Page Style menu. Focus
# should be on the "No Style" radio menu item.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar View Page Style & y No Style RadioItem'
#      VISIBLE:  '& y No Style RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'No Style not selected radio menu item'
#
sequence.append(TypeAction("y"))
sequence.append(WaitForFocus("No Style", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# Note: Due to https://bugzilla.mozilla.org/show_bug.cgi?id=396799,
# We might not speak the item count.
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar View Page Style & y No Style RadioItem'
#      VISIBLE:  '& y No Style RadioItem', cursor=1
# SPEECH OUTPUT: 'Page Style menu'
# SPEECH OUTPUT: 'No Style'
# SPEECH OUTPUT: 'radio menu item'
# SPEECH OUTPUT: 'not selected'
# SPEECH OUTPUT: 'item 1 of 2'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Down Arrow to the "Basic Page Style" radio menu item. The following
# should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar View Page Style &=y Basic Page Style RadioItem'
#      VISIBLE:  '&=y Basic Page Style RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Basic Page Style selected radio menu item'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Basic Page Style", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# Note: Due to https://bugzilla.mozilla.org/show_bug.cgi?id=396799,
# We might not speak the item count.
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar View Page Style &=y Basic Page Style RadioItem'
#      VISIBLE:  '&=y Basic Page Style RadioItem', cursor=1
# SPEECH OUTPUT: 'Page Style menu item'
# SPEECH OUTPUT: 'Basic Page Style'
# SPEECH OUTPUT: 'radio menu item'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: 'item 2 of 2'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the "Page Style" menu by pressing Escape.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Page Style", acc_role=pyatspi.ROLE_MENU))

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
