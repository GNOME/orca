#!/usr/bin/python

"""Test of entry output using Firefox.
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
# Press Shift+F10 to bring up a context menu then Down Arrow once to
# get to "New Bookmark..." and press Return.
#
sequence.append(KeyComboAction("<Shift>F10"))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("New Bookmark...", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))

########################################################################
# Note:  I'm getting inconsistent results in the playback.  For instance
# sometimes we type the initial letter in the TypeAction string twice.
# Sometimes the speech and braille for deleted text seems to be based
# on starting at a different location.  Therefore, I'm adding delays
# and pauses in key locations in the hopes of giving everything enough
# time to "catch up."
#
sequence.append(PauseAction(1000))

########################################################################
# Focus will be in the Name single-line entry.  Type "this is a test"
#
# After it is all written, the following appears in braille.  (Key
# echo handles the speech.)
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a test $l'
#      VISIBLE:  'this is a test $l', cursor=14
# 
sequence.append(WaitForFocus("Name:", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("this is a test"))

########################################################################
# Backspace 5 times (thus removing "<space>test" from the right)
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a test $l'
#      VISIBLE:  'this is a test $l', cursor=15
# SPEECH OUTPUT: 't'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a tes $l'
#      VISIBLE:  'this is a tes $l', cursor=14
# SPEECH OUTPUT: 's'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a te $l'
#      VISIBLE:  'this is a te $l', cursor=13
# SPEECH OUTPUT: 'e'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a t $l'
#      VISIBLE:  'this is a t $l', cursor=12
# SPEECH OUTPUT: 't'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a  $l'
#      VISIBLE:  'this is a  $l', cursor=11
# SPEECH OUTPUT: ' '
#
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))

########################################################################
# Control Backspace 3 times thus removing "this is a" word by word from
# the right.
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a $l'
#      VISIBLE:  'this is a $l', cursor=9
# SPEECH OUTPUT: 'a'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is  $l'
#      VISIBLE:  'this is  $l', cursor=6
# SPEECH OUTPUT: 'is '
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this  $l'
#      VISIBLE:  'this  $l', cursor=1
# SPEECH OUTPUT: 'this '
#
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(KeyComboAction("<Control>BackSpace"))

########################################################################
# Type "so is this"
#
# After it is all written, the following appears in braille.  (Key
# echo handles the speech.)
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=11
#
sequence.append(PauseAction(1000))
sequence.append(TypeAction("so is this"))

########################################################################
# Press Left Arrow 4 times to get to the beginning of "this"
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=10
# SPEECH OUTPUT: 's'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=9
# SPEECH OUTPUT: 'i'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=8
# SPEECH OUTPUT: 'h'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=7
# SPEECH OUTPUT: 't'
#
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))

########################################################################
# Press Control Left Arrow twice to get to the beginning of the 
# line.
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=4
# SPEECH OUTPUT: 'is '
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=1
# SPEECH OUTPUT: 'so '
#
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(KeyComboAction("<Control>Left"))

########################################################################
# Press Control Delete twice to get rid of "so is".  [[[Bug:  We are
# speaking the new caret location -- we land on a space -- rather than
# the word that was just deleted.]]] 
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'
#      VISIBLE:  'so is this $l', cursor=3
# SPEECH OUTPUT: ' '
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  is this $l'
#      VISIBLE:  ' is this $l', cursor=4
# SPEECH OUTPUT: ' '
#
sequence.append(KeyComboAction("<Control>Delete", 500))
sequence.append(KeyComboAction("<Control>Delete", 500))

########################################################################
# Press Delete 5 times to delete "<space>this".  [[[Note:  I don't get
# why I'm getting the following for the speech and braille.  When
# I perform the test manually, Orca correctly speaks the current
# character.  When I run the test using runone.sh, but with Orca 
# launched first, I also get the expected output. Here it seems to be 
# speaking the character that was just deleted.]]]
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  this $l'
#      VISIBLE:  ' this $l', cursor=1
# SPEECH OUTPUT: ' '
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this $l'
#      VISIBLE:  'this $l', cursor=1
# SPEECH OUTPUT: 't'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog his $l'
#      VISIBLE:  'his $l', cursor=1
# SPEECH OUTPUT: 'h'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog is $l'
#      VISIBLE:  'is $l', cursor=1
# SPEECH OUTPUT: 'i'
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog s $l'
#      VISIBLE:  's $l', cursor=1
# SPEECH OUTPUT: 's'
#
sequence.append(KeyComboAction("Delete", 500))
sequence.append(KeyComboAction("Delete", 500))
sequence.append(KeyComboAction("Delete", 500))
sequence.append(KeyComboAction("Delete", 500))
sequence.append(KeyComboAction("Delete", 500))

########################################################################
# Press Tab to get to the Location entry.
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'
#      VISIBLE:  ' $l', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Location: text '
#
sequence.append(KeyComboAction("Tab", 1000))
sequence.append(WaitForFocus("Location:", acc_role=pyatspi.ROLE_ENTRY))

########################################################################
# Press Tab to get to the Keyword entry.
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Keyword: text '
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Keyword:", acc_role=pyatspi.ROLE_ENTRY))

########################################################################
# Press Tab to get to the Description entry.
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Description: text '
#

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Description:", acc_role=pyatspi.ROLE_ENTRY))

########################################################################
# Type "Here is the first line."  Press Return.  
#
# After it is all written, the following appears in braille.  (Key
# echo handles the speech.)
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first line $l'
#      VISIBLE:  'Here is the first line $l', cursor=22
#
sequence.append(TypeAction("Here is the first line."))
sequence.append(KeyComboAction("Return"))

########################################################################
# Type "Here is the second line."
#
# After it is all written, the following appears in braille.  (Key
# echo handles the speech.)
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line. $l'
#      VISIBLE:  'Here is the second line. $l', cursor=25
#
sequence.append(TypeAction("Here is the second line."))

########################################################################
# Press Up Arrow to read the first line.
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first line. $l'
#      VISIBLE:  'Here is the first line. $l', cursor=24
# SPEECH OUTPUT: 'Here is the first line.'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Press Down Arrow to read the first line.
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line. $l'
#      VISIBLE:  'Here is the second line. $l', cursor=25
# SPEECH OUTPUT: 'Here is the second line.'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Press KP_Enter to get where am I information for this item. 
#
# BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line. $l'
#      VISIBLE:  'Here is the second line. $l', cursor=25
# SPEECH OUTPUT: 'Here is the first line.
# Here is the second line.'
# SPEECH OUTPUT: 'text'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Escape to dismiss the dialog.  Focus should return to the
# Places Organizer.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForWindowActivate("Places Organizer",None))

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
