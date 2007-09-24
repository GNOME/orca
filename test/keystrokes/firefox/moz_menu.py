#!/usr/bin/python

"""Test of Mozilla ARIA menu presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Accessible DHTML" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA spreadsheet demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/spreadsheet"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Accessible DHTML", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Move to the menu.  The following will be presented.
#
# BRAILLE LINE:  'Edit'
#      VISIBLE:  'Edit', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Edit'
#
sequence.append(KeyComboAction("<Control><Alt>m"))
sequence.append(WaitForFocus("Edit", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Edit'
#      VISIBLE:  'Edit', cursor=1
# SPEECH OUTPUT: 'Edit section'
# SPEECH OUTPUT: 'Edit'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 1 of 1'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
########################################################################
# Use arrows to navigate menu structure.  The following will be presented
# for each move.
#
# BRAILLE LINE:  'Edit View'
#      VISIBLE:  'Edit View', cursor=6
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'View'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("View", acc_role=pyatspi.ROLE_MENU_ITEM))

# Note:  accessible name needed to be removed because of unicode characters
# BRAILLE LINE:  'Themes          >'
#      VISIBLE:  'Themes          >', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Themes          >'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'Themes          > Basic Grey '
#      VISIBLE:  'Themes          > Basic Gr', cursor=19
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Basic Grey '
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Basic Grey", acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'The Blues'
#      VISIBLE:  'The Blues', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'The Blues'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("The Blues", acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'Garden'
#      VISIBLE:  'Garden', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Garden'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Garden", acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'In the Pink grayed'
#      VISIBLE:  'In the Pink grayed', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'In the Pink grayed'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("In the Pink", acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'Rose '
#      VISIBLE:  'Rose ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Rose '
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Rose", acc_role=pyatspi.ROLE_MENU_ITEM))

# Note:  accessible name needed to be removed because of unicode characters
# BRAILLE LINE:  'Themes          >'
#      VISIBLE:  'Themes          >', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Themes          >'
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'Hide'
#      VISIBLE:  'Hide', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Hide'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Hide", acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'Show'
#      VISIBLE:  'Show', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Show", acc_role=pyatspi.ROLE_MENU_ITEM))

# Note:  accessible name needed to be removed because of unicode characters
# BRAILLE LINE:  'More                >'
#      VISIBLE:  'More                >', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'More                >'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'More                > one '
#      VISIBLE:  'More                > o', cursor=23
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'one '
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("one", acc_role=pyatspi.ROLE_MENU_ITEM))

# BRAILLE LINE:  'two'
#      VISIBLE:  'two', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'two'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("two", acc_role=pyatspi.ROLE_MENU_ITEM))

# Leave the menu.  Focus moves to the first cell of the table.
# BRAILLE LINE:  'Entry # Date Expense Amount Merchant Type ColumnHeader'
#      VISIBLE:  'Entry # Date Expense Amount Merc', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Entry # column header'
sequence.append(KeyComboAction("Escape"))

########################################################################
# End menu navigation
#

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
