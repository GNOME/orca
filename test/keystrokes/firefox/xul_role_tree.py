#!/usr/bin/python

"""Test of tree output using Firefox.
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
# We wait for the focus to be in the Places Organizer window.
#
sequence.append(WaitForWindowActivate("Places Organizer",None))

########################################################################
# Press Shift+Tab to move to the tree of bookmarks on the left.  Note
# that this item is expanded and contains 3 items. [[[Bug:  We're not
# handling list items in trees approriately for during navigation or
# where am I.  I've created a patch for this.  See bug #480021.  The
# output that follows is what we get without the patch, just so that
# this widget is covered "for now".]]]
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Bookmarks expanded ListItem LEVEL 1'
#      VISIBLE:  'Bookmarks expanded ListItem LEVE', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Bookmarks'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Bookmarks", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Down Arrow to give focus to the first item within the Bookmarks
# folder, Bookmarks Toolbar Folder.
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Bookmarks Toolbar Folder ListItem LEVEL 2'
#      VISIBLE:  'Bookmarks Toolbar Folder ListIte', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Bookmarks Toolbar Folder'
# SPEECH OUTPUT: 'tree level 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Bookmarks Toolbar Folder", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Down Arrow to give focus to the second item within the Bookmarks
# folder, GNOME.  Note that this item is expandable but collapsed.  See
# comment above.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree GNOME ListItem LEVEL 2'
#      VISIBLE:  'GNOME ListItem LEVEL 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'GNOME'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("GNOME", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Down Arrow to give focus to the third item within the Bookmarks
# folder, Mozilla.  Note that this item is expandable but collapsed.
# See comment above.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Mozilla collapsed ListItem LEVEL 2'
#      VISIBLE:  'Mozilla collapsed ListItem LEVEL', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mozilla'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Mozilla", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press KP_Enter to get where am I information for this item.  See
# coment above.
# 
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Mozilla collapsed ListItem LEVEL 2'
#      VISIBLE:  'Mozilla collapsed ListItem LEVEL', cursor=1
# SPEECH OUTPUT: 'Mozilla'
# SPEECH OUTPUT: 'list item'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Right Arrow to expand Mozilla.  See comment above.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Mozilla collapsed ListItem LEVEL 2'
#      VISIBLE:  'Mozilla collapsed ListItem LEVEL', cursor=1
# SPEECH OUTPUT: 'Mozilla'
#
sequence.append(KeyComboAction("Right"))

########################################################################
# Press KP_Enter to get where am I information for this item.  See
# coment above.
# 
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Mozilla expanded ListItem LEVEL 2'
#      VISIBLE:  'Mozilla expanded ListItem LEVEL ', cursor=1
# SPEECH OUTPUT: 'Mozilla'
# SPEECH OUTPUT: 'list item'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Down Arrow to move to the first item within it, Firefox.  Note
# that Firefox is expandable but collapsed.  See comment above.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Firefox ListItem LEVEL 3'
#      VISIBLE:  'Firefox ListItem LEVEL 3', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Firefox'
# SPEECH OUTPUT: 'tree level 3'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Firefox", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Up Arrow to return to Mozilla.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Mozilla expanded ListItem LEVEL 2'
#      VISIBLE:  'Mozilla expanded ListItem LEVEL ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mozilla'
# SPEECH OUTPUT: 'tree level 2'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Mozilla", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Press Left Arrow to collapse Mozilla.  See comment above.
#
# BRAILLE LINE:  'Minefield Application Places Organizer Frame Tree Mozilla collapsed ListItem LEVEL 2'
#      VISIBLE:  'Mozilla collapsed ListItem LEVEL', cursor=1
# SPEECH OUTPUT: 'Mozilla'
#
sequence.append(KeyComboAction("Left"))

########################################################################
# Press Tab to return to the tree table that had focus initially.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Firefox", acc_role=pyatspi.ROLE_TABLE_CELL))

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
