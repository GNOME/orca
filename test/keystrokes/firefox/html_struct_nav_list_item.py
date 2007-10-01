#!/usr/bin/python

"""Test of HTML list output of Firefox, in particular structural
navigation by list item.
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
# Press L to move to the first list. Note:  Because these are HTML 
# (un)ordered lists, we are not going to be getting any focus events.  
# Therefore we have to use pause actions instead.  
#
# SPEECH OUTPUT: 'List with 4 items'
# BRAILLE LINE:  '1. remember what the heck we are doing each day'
#      VISIBLE:  '1. remember what the heck we are', cursor=1
# SPEECH OUTPUT: '1. remember what the heck we are doing each day'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press L to move to the second list.
#
# SPEECH OUTPUT: 'List with 6 items'
# BRAILLE LINE:  'VI. And use roman numerals,'
#      VISIBLE:  'VI. And use roman numerals,', cursor=1
# SPEECH OUTPUT: 'VI. And use roman numerals,'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press L to move to the third list.
#
# SPEECH OUTPUT: 'List with 2 items'
# BRAILLE LINE:  '* listing item'
#      VISIBLE:  '* listing item', cursor=1
# SPEECH OUTPUT: '* listing item'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press I to move among all of the items (sub items, sub sub items, 
# etc.) in the third list.
#
# BRAILLE LINE:  '* first sublevel'
#      VISIBLE:  '* first sublevel', cursor=1
# SPEECH OUTPUT: '* first sublevel'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* look for the bullet on'
#      VISIBLE:  '* look for the bullet on', cursor=1
#SPEECH OUTPUT:  '* look for the bullet on'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* each sublevel'
#      VISIBLE:  '* each sublevel', cursor=1
# SPEECH OUTPUT: '* each sublevel'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  ' they should all be different, except here.'
#      VISIBLE:  ' they should all be different', cursor=1
# SPEECH OUTPUT: ' they should all be different, except here.'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* second sublevel'
#      VISIBLE:  '* second sublevel', cursor=1
# SPEECH OUTPUT: '* second sublevel'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* or you can specify a square'
#      VISIBLE:  '* or you can specify a square', cursor=1
# SPEECH OUTPUT: '* or you can specify a square'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* if your TYPE is circle'
#      VISIBLE:  '* if your TYPE is circle', cursor=1
# SPEECH OUTPUT: '* if your TYPE is circle'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* or even a disc'
#      VISIBLE:  '* or even a disc', cursor=1
# SPEECH OUTPUT: '* or even a disc'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* Franz Liszt'
#      VISIBLE:  '* Franz Liszt', cursor=1
# PEECH OUTPUT:  '* Franz Liszt'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* was a composer who was not square'
#      VISIBLE:  '* was a composer who was not s', cursor=1
# SPEECH OUTPUT: '* was a composer who was not square'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* would have liked the Who'
#      VISIBLE:  '* would have liked the Who', cursor=1
# SPEECH OUTPUT: '* would have liked the Who'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* feeling listless'
#      VISIBLE:  '* feeling listless', cursor=1
# SPEECH OUTPUT: '* feeling listless'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* blah, blah, blah'
#      VISIBLE:  '* blah, blah, blah', cursor=1
# SPEECH OUTPUT: '* blah, blah, blah'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* whine, whine, whine'
#      VISIBLE:  '* whine, whine, whine', cursor=1
# SPEECH OUTPUT: '* whine, whine, whine'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'Wrapping to top.'
# BRAILLE LINE:  '1. remember what the heck we are doing each day'
#      VISIBLE:  '1. remember what the heck we are', cursor=1
# SPEECH OUTPUT: '1. remember what the heck we are doing each day'
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '2. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some '
#      VISIBLE:  '2. arrange long and arbitrary li', cursor=1
# SPEECH OUTPUT: '2. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some '
#
sequence.append(KeyComboAction("i"))
sequence.append(PauseAction(1000))

########################################################################
# Now reverse our direction, but just for a few items.
#
# BRAILLE LINE:  '1. remember what the heck we are doing each day'
#      VISIBLE:  '1. remember what the heck we are', cursor=1
# SPEECH OUTPUT: '1. remember what the heck we are doing each day'
#
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'Wrapping to bottom.'
# BRAILLE LINE:  '* whine, whine, whine'
#      VISIBLE:  '* whine, whine, whine', cursor=1
# SPEECH OUTPUT: '* whine, whine, whine'
#
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* blah, blah, blah'
#      VISIBLE:  '* blah, blah, blah', cursor=1
# SPEECH OUTPUT: '* blah, blah, blah'
#
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(PauseAction(1000))

# BRAILLE LINE:  '* feeling listless'
#      VISIBLE:  '* feeling listless', cursor=1
# SPEECH OUTPUT: '* feeling listless'
#
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(PauseAction(1000))

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
