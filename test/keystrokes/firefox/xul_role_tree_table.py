#!/usr/bin/python

"""Test of tree table output using Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "Bookmarks" menu, Down Arrow to Organize Bookmarks, then 
# press Return.
#
sequence.append(KeyComboAction("<Alt>b"))
sequence.append(WaitForFocus("Bookmarks", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Bookmark This Page...", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Organize Bookmarks...", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))

########################################################################
# We wait for the focus to be in the Places Organizer window
#
sequence.append(WaitForWindowActivate("Places Organizer",None))

########################################################################
# Press Down Arrow to get to the first item in the tree.  The first
# item is named GNOME, it is collapsed.  Up to this point, we're not
# in the tree either, so when focus moves there, we speak the column
# header of the cell that just gained focus. [[[Bug?  We're showing
# the level of each item in the column.  The other columns are empty
# but we still have "TREE LEVEL 1"s for each of them.  Should we?]]]
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader GNOME collapsed TREE LEVEL 1  TREE LEVEL 1  TREE LEVEL 1'
#     VISIBLE:  'GNOME collapsed TREE LEVEL 1  TR', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Name column header'
# SPEECH OUTPUT: 'GNOME collapsed  '
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("GNOME", acc_role=pyatspi.ROLE_TABLE_CELL))

########################################################################
# Press Down Arrow to get to the second item in the tree.  Its name is
# Mozilla.  It is also collapsed.  And it's at the same level as GNOME
# so we should not speak the level.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Mozilla collapsed TREE LEVEL 1  TREE LEVEL 1  TREE LEVEL 1'
#      VISIBLE:  'Mozilla collapsed TREE LEVEL 1  ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mozilla collapsed  '
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Mozilla", acc_role=pyatspi.ROLE_TABLE_CELL))

########################################################################
# Press KP_Enter to get where am I information for this item.
# 
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Mozilla collapsed TREE LEVEL 1'
#      VISIBLE:  'Mozilla collapsed TREE LEVEL 1', cursor=1 
# SPEECH OUTPUT: 'Mozilla'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'row 3 of 4'
# SPEECH OUTPUT: 'collapsed'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Right Arrow to expand the Mozilla tree item.
# 
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Mozilla expanded TREE LEVEL 1'
#      VISIBLE:  'Mozilla expanded TREE LEVEL 1', cursor=1
# SPEECH OUTPUT: 'Mozilla expanded 5 items'
#
sequence.append(KeyComboAction("Right"))

########################################################################
# Press KP_Enter to get where am I information for this item now
# that it is expanded.
# 
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Mozilla expanded TREE LEVEL 1'
#      VISIBLE:  'Mozilla expanded TREE LEVEL 1', cursor=1 
# SPEECH OUTPUT: 'Mozilla'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'row 3 of 9'
# SPEECH OUTPUT: 'expanded'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Down Arrow to move to the first item in Mozilla.  Its name
# is Firefox and it is expandable.  Because we're changing levels,
# we should also have level information spoken.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Firefox collapsed TREE LEVEL 2  TREE LEVEL 2  TREE LEVEL 2'
#      VISIBLE:  'Firefox collapsed TREE LEVEL 2  ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Firefox collapsed  '
# SPEECH OUTPUT: 'tree level 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Firefox", acc_role=pyatspi.ROLE_TABLE_CELL))

########################################################################
# Press Down Arrow to move to the second item in Mozilla.  Its name
# is Thunderbird and it is expandable. 
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Thunderbird collapsed TREE LEVEL 2  TREE LEVEL 2  TREE LEVEL 2'
#      VISIBLE:  'Thunderbird collapsed TREE LEVEL', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Thunderbird collapsed  '
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Thunderbird", acc_role=pyatspi.ROLE_TABLE_CELL))

########################################################################
# Press Down Arrow to move to the third item in Mozilla.  Its name
# is Mozilla Accessibility Project.  It is not expandable.  It also
# has a URL showing for it.
# 
#  BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Mozilla Accessibility Project TREE LEVEL 2  TREE LEVEL 2 http://www.mozilla.org/access/ TREE LEVEL 2'
#      VISIBLE:  'Mozilla Accessibility Project TR', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mozilla Accessibility Project  http://www.mozilla.org/access/'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Mozilla Accessibility Project", acc_role=pyatspi.ROLE_TABLE_CELL))

########################################################################
# Press KP_Enter to get where am I information for this item.
# 
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Mozilla Accessibility Project TREE LEVEL 2'
#      VISIBLE:  'Mozilla Accessibility Project TR', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: 'Mozilla Accessibility Project'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'http://www.mozilla.org/access/'
# SPEECH OUTPUT: 'row 6 of 9'
#

########################################################################
# Press Up Arrow three times to return to the Mozilla row.
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Thunderbird", acc_role=pyatspi.ROLE_TABLE_CELL))

sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Firefox", acc_role=pyatspi.ROLE_TABLE_CELL))

sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Mozilla", acc_role=pyatspi.ROLE_TABLE_CELL))

########################################################################
# Press Left Arrow to collapse the Mozilla tree item.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame ScrollPane TreeTable Name ColumnHeader Mozilla collapsed TREE LEVEL 1'
#      VISIBLE:  'Mozilla collapsed TREE LEVEL 1', cursor=1
# SPEECH OUTPUT: 'Mozilla collapsed'
#
sequence.append(KeyComboAction("Left"))

########################################################################
# Now that the Places Manager is back to its pre-explored state,
# press Alt F4 to close it.
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Wait for the focus to be back on the blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
