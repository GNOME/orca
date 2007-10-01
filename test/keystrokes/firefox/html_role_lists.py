#!/usr/bin/python

"""Test of HTML list output of Firefox, in particular basic navigation
and where am I.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local combo box test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "lists.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Lists Test Page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Down Arrow until the first list is reached.  Note:  Because
# these are HTML (un)ordered lists, we are not going to be getting any 
# focus events.  Therefore we have to use pause actions instead.  Note
# if I choose a small pause action value, the list items seem to get
# messed up, EOC's appear, and all the list items are numbered (0).
# Things seem more likely to be okay at 3000, however I'm still
# not getting 100% reliable results.  This problem does not occur when
# I access lists using Orca manually.
#
# BRAILLE LINE:  'Lists are not only fun to make, they are fun to use. They help us: '
#      VISIBLE:  'Lists are not only fun to make, ', cursor=1
# SPEECH OUTPUT: 'Lists are not only fun to make, they are fun to use. They help us: '
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

########################################################################
# Start of first list.  Keep going down.
#
# BRAILLE LINE:  '1. remember what the heck we are doing each day'
#      VISIBLE:  '1. remember what the heck we are', cursor=1
# SPEECH OUTPUT: '1. remember what the heck we are doing each day'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  '2. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of '
#      VISIBLE:  '2. arrange long and arbitrary li', cursor=1
# SPEECH OUTPUT: '2. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of '
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  '3. look really cool when we carry them around on yellow Post-Itstm.'
#      VISIBLE:  '3. look really cool when we carr', cursor=1
# SPEECH OUTPUT: '3. look really cool when we carry them around on yellow Post-Itstm.'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  '4. and that other thing I keep forgetting.'
#      VISIBLE:  '4. and that other thing I keep f', cursor=1
# SPEECH OUTPUT: '4. and that other thing I keep forgetting.'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

########################################################################
# Start of second list.  Keep going down.
#
# BRAILLE LINE:  'VI. And use roman numerals,'
#      VISIBLE:  'VI. And use roman numerals,', cursor=1
# SPEECH OUTPUT: 'VI. And use roman numerals,'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  'g. You might try using letters as well,'
#      VISIBLE:  'g. You might try using letters a', cursor=1
# SPEECH OUTPUT: 'g. You might try using letters as well,'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  'H. Maybe you prefer Big Letters,'
#      VISIBLE:  'H. Maybe you prefer Big Letters,', cursor=1
# SPEECH OUTPUT: 'H. Maybe you prefer Big Letters,'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  'ix. or small roman numerals'
#      VISIBLE:  'ix. or small roman numerals', cursor=1
# SPEECH OUTPUT: 'ix. or small roman numerals'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  '* But discs belong to unordered lists'
#      VISIBLE:  '* But discs belong to unordere', cursor=1
# SPEECH OUTPUT: '* But discs belong to unordered lists'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  '50. Though you can set the value in a list item!'
#      VISIBLE:  '50. Though you can set the value', cursor=1
# SPEECH OUTPUT: '50. Though you can set the value in a list item!'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

########################################################################
# Start of third list.  Keep going down -- at least far enough to get
# into a nested list or two.
#
# BRAILLE LINE:  '* listing item'
#      VISIBLE:  '* listing item', cursor=1
# SPEECH OUTPUT: '* listing item'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

########################################################################
# Start of the first sub-list in the third list. [[[Mike:  When we
# arrow through list items -- as opposed to use structural navigation
# within them -- we don't speak level information.  Should we be
# doing this?]]]
#
# BRAILLE LINE:  '* first sublevel'
#      VISIBLE:  '* first sublevel', cursor=1
# SPEECH OUTPUT: '* first sublevel'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

########################################################################
# Start of the first sub-sub-list in the third list. 
#
# BRAILLE LINE:  '* look for the bullet on'
#      VISIBLE:  '* look for the bullet on', cursor=1
# SPEECH OUTPUT: '* look for the bullet on'
#
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

########################################################################
# Press Up Arrow a couple of times just to be sure we read correctly 
# in both directions.
#
# BRAILLE LINE:  '* first sublevel'
#      VISIBLE:  '* first sublevel', cursor=1
# SPEECH OUTPUT: '* first sublevel'
#
sequence.append(KeyComboAction("Up"))
sequence.append(PauseAction(3000))

# BRAILLE LINE:  '* listing item'
#      VISIBLE:  '* listing item', cursor=1
# SPEECH OUTPUT: '* listing item'
#
sequence.append(KeyComboAction("Up"))
sequence.append(PauseAction(3000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
# BRAILLE LINE:  '* listing item'
#      VISIBLE:  '* listing item', cursor=1
# SPEECH OUTPUT: '* listing item''
# SPEECH OUTPUT: 'list item'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l", 1000))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
