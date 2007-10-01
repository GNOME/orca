#!/usr/bin/python

"""Test of HTML list output of Firefox, in particular structural
navigation by list.
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
# Press L to move to the first sub-list of the third list.
#
# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 1'
# BRAILLE LINE:  '* first sublevel'
#      VISIBLE:  '* first sublevel', cursor=1
# SPEECH OUTPUT: '* first sublevel'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press L to move to the first list *within* the first sub-list of
# the third list.
#
# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 2'
# BRAILLE LINE:  '* look for the bullet on'
#      VISIBLE:  '* look for the bullet on', cursor=1
# SPEECH OUTPUT: '* look for the bullet on'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press L again.  To move to the first sub-sub-list of the third list.
# Phew, that's the inner-most list.
#
# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 3'
# BRAILLE LINE:  '* each sublevel'
#      VISIBLE:  '* each sublevel', cursor=1
# SPEECH OUTPUT: '* each sublevel'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press L again.  Now we're working our way out, but still stopping
# on the first item of each new list we come across.
#
# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 2'
# BRAILLE LINE:  '* if your TYPE is circle'
#      VISIBLE:  '* if your TYPE is circle', cursor=1
# SPEECH OUTPUT: '* if your TYPE is circle'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press L again.  Almost done.
#
# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 1'
# BRAILLE LINE:  '* was a composer who was not square'
#      VISIBLE:  '* was a composer who was not s', cursor=1
# SPEECH OUTPUT: '* was a composer who was not square'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Press L again.  That should be all of the lists.
#
# SPEECH OUTPUT: 'List with 3 items'
# BRAILLE LINE:  '* feeling listless'
#      VISIBLE:  '* feeling listless', cursor=1
# SPEECH OUTPUT: '* feeling listless'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Pressing L again should result in our wrapping to the top.
#
# SPEECH OUTPUT: 'Wrapping to top.'
# SPEECH OUTPUT: 'List with 4 items'
# BRAILLE LINE:  '1. remember what the heck we are doing each day'
#      VISIBLE:  '1. remember what the heck we are', cursor=1
# SPEECH OUTPUT: '1. remember what the heck we are doing each day'
#
sequence.append(KeyComboAction("l"))
sequence.append(PauseAction(1000))

########################################################################
# Pressing Shift+L again should result in our wrapping to the bottom
# and then landing on the first item in the last list on the page.
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

########################################################################
# Pressing Shift+L subsequently should place us on all of the lists
# we found by pressing L, but in the reverse direction.
#
# SPEECH OUTPUT: 'Wrapping to bottom.'
# SPEECH OUTPUT: 'List with 3 items'
# BRAILLE LINE:  '* feeling listless'
#      VISIBLE:  '* feeling listless', cursor=1
# SPEECH OUTPUT: '* feeling listless'
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 1'
# BRAILLE LINE:  '* was a composer who was not square'
#      VISIBLE:  '* was a composer who was not s', cursor=1
# SPEECH OUTPUT: '* was a composer who was not square'
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 2'
# BRAILLE LINE:  '* if your TYPE is circle'
#      VISIBLE:  '* if your TYPE is circle', cursor=1
# SPEECH OUTPUT: '* if your TYPE is circle'
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 3'
# BRAILLE LINE:  '* each sublevel'
#       VISIBLE: '* each sublevel', cursor=1
# SPEECH OUTPUT: '* each sublevel'
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 2'
# BRAILLE LINE:  '* look for the bullet on'
#      VISIBLE:  '* look for the bullet on', cursor=1
# SPEECH OUTPUT: '* look for the bullet on'
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'List with 2 items'
# SPEECH OUTPUT: 'Nesting level 1'
# BRAILLE LINE:  '* first sublevel'
#      VISIBLE:  '* first sublevel', cursor=1
# SPEECH OUTPUT: '* first sublevel'
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'List with 6 items'
# BRAILLE LINE:  'VI. And use roman numerals,'
#      VISIBLE:  'VI. And use roman numerals,', cursor=1
# SPEECH OUTPUT: 'VI. And use roman numerals,'
#
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(PauseAction(1000))

# SPEECH OUTPUT: 'List with 4 items'
# BRAILLE LINE:  '1. remember what the heck we are doing each day'
#      VISIBLE:  '1. remember what the heck we are', cursor=1
# SPEECH OUTPUT: '1. remember what the heck we are doing each day'
#
sequence.append(KeyComboAction("<Shift>l"))
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
