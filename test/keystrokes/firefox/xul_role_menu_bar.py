#!/usr/bin/python

"""Test of menu bar output of Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# [[[BUG: Sometimes menus on the menu bar in Firefox are claiming to be
# menu items. See https://bugzilla.mozilla.org/show_bug.cgi?id=396799]]]
#

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu.  Focus is on the "New Window" menu item.  We
# get a focus event for the menu, then one for the menu item.
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar File'
#      VISIBLE:  'File', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'File'
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar File New Window(Control N)'
#      VISIBLE:  'New Window(Control N)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'New Window Control N'
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Right Arrow to the "Edit" menu.  [[[Bug?  When you arrow from menu
# to menu on the menu bar, whatever had focus before claims it again
# before the next menu -- or really menu item -- gains focus.  This
# is annoying.  I'll file a bug against Mozilla asking if those
# events are really necessary.]]] After focus momentarily goes to the
# Location autocomplete, it's claimed by the Edit menu.  Finally, the
# Select All menu item in the Edit menu claims focus.  (Yes, all from
# one little press of Right Arrow).
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar AutoComplete Location  $l'
#      VISIBLE:  'Location  $l', cursor=10
# SPEECH OUTPUT: 'Location autocomplete'
# SPEECH OUTPUT: 'Location text '
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Edit'
#      VISIBLE:  'Edit', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Edit'
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Edit Select All(Control A)'
#      VISIBLE:  'Select All(Control A)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Select All Control A'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Select All", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Right Arrow to the "View" menu.  Focus is on the Toolbars menu. 
# See above comments regarding menus that claim to be menu items and
# the repeated focus events for the Location Autocomplete.
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar AutoComplete Location  $l'
#      VISIBLE:  'Location  $l', cursor=10
# SPEECH OUTPUT: 'Location autocomplete'
# SPEECH OUTPUT: 'Location text '
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar View'
#      VISIBLE:  'View', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'View'
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar View Toolbars'
#      VISIBLE:  'Toolbars', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Toolbars'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Toolbars", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Left Arrow back to the "Edit" menu.  Focus is on the "Select All" 
# menu item. See above comments.
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar AutoComplete Location  $l'
#      VISIBLE:  'Location  $l', cursor=10
# SPEECH OUTPUT: 'Location autocomplete'
# SPEECH OUTPUT: 'Location text '
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Edit'
#      VISIBLE:  'Edit', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Edit'
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Edit Select All(Control A)'
#      VISIBLE:  'Select All(Control A)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Select All Control A'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Select All", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Left Arrow back to the "File" menu.  Focus is on the "New Window"
# menu item.  See above comments.
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar AutoComplete Location  $l'
#      VISIBLE:  'Location  $l', cursor=10
# SPEECH OUTPUT: 'Location autocomplete'
# SPEECH OUTPUT: 'Location text '
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar File'
#      VISIBLE:  'File', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'File'
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar File New Window(Control N)'
#      VISIBLE:  'New Window(Control N)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'New Window Control N'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

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
