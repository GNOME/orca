# -*- coding: utf-8 -*-
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
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local lists test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "lists.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Lists Test Page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Welcome to a List of Lists h1'",
     "     VISIBLE:  'Welcome to a List of Lists h1', cursor=1",
     "BRAILLE LINE:  'Welcome to a List of Lists h1'",
     "     VISIBLE:  'Welcome to a List of Lists h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to a List of Lists heading level 1'"]))

########################################################################
# Press L to move to the first list. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to first list",
    ["BRAILLE LINE:  'List with 4 items'",
     "     VISIBLE:  'List with 4 items', cursor=0",
     "BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: 'List with 4 items'",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

########################################################################
# Press L to move to the second list.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to second list", 
    ["BRAILLE LINE:  'List with 6 items'",
     "     VISIBLE:  'List with 6 items', cursor=0",
     "BRAILLE LINE:  'VI.And use roman numerals,'",
     "     VISIBLE:  'VI.And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: 'List with 6 items'",
     "SPEECH OUTPUT: 'VI.And use roman numerals,'"]))

########################################################################
# Press L to move to the third list.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to third list",
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  '•listing item'",
     "     VISIBLE:  '•listing item', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '•listing item'"]))

########################################################################
# Press L to move to the first sub-list of the third list.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to third list's first sub list",
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 1'",
     "     VISIBLE:  'Nesting level 1', cursor=0",
     "BRAILLE LINE:  '◦first sublevel'",
     "     VISIBLE:  '◦first sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: '◦first sublevel'"]))

########################################################################
# Press L to move to the first list *within* the first sub-list of
# the third list.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to third list's first sub list's first list", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 2'",
     "     VISIBLE:  'Nesting level 2', cursor=0",
     "BRAILLE LINE:  '▪look for the bullet on'",
     "     VISIBLE:  '▪look for the bullet on', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: '▪look for the bullet on'"]))

########################################################################
# Press L again.  To move to the first sub-sub-list of the third list.
# Phew, that's the inner-most list.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to third list's inner-most list", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 3'",
     "     VISIBLE:  'Nesting level 3', cursor=0",
     "BRAILLE LINE:  '▪each sublevel'",
     "     VISIBLE:  '▪each sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 3'",
     "SPEECH OUTPUT: '▪each sublevel'"]))

########################################################################
# Press L again.  Now we're working our way out, but still stopping
# on the first item of each new list we come across.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to next sub list in the third list",
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 2'",
     "     VISIBLE:  'Nesting level 2', cursor=0",
     "BRAILLE LINE:  '◦if your TYPE is circle'",
     "     VISIBLE:  '◦if your TYPE is circle', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: '◦if your TYPE is circle'"]))

########################################################################
# Press L again.  Almost done.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to next sub list in the third list",
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 1'",
     "     VISIBLE:  'Nesting level 1', cursor=0",
     "BRAILLE LINE:  '◦was a composer who was not square'",
     "     VISIBLE:  '◦was a composer who was not squa', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: '◦was a composer who was not square'"]))

########################################################################
# Press L again.  That should be all of the lists.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l to last sub list in the third list",
    ["BRAILLE LINE:  'List with 3 items'",
     "     VISIBLE:  'List with 3 items', cursor=0",
     "BRAILLE LINE:  '◦feeling listless'",
     "     VISIBLE:  '◦feeling listless', cursor=1",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '◦feeling listless'"]))

########################################################################
# Pressing L again should result in our wrapping to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "l - should wrap to top", 
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'List with 4 items'",
     "     VISIBLE:  'List with 4 items', cursor=0",
     "BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'List with 4 items'",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

########################################################################
# Pressing Shift+L should result in our wrapping to the bottom
# and then landing on the first item in the last list on the page.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l - should wrap to bottom",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'List with 3 items'",
     "     VISIBLE:  'List with 3 items', cursor=0",
     "BRAILLE LINE:  '◦feeling listless'",
     "     VISIBLE:  '◦feeling listless', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '◦feeling listless'"]))

########################################################################
# Pressing Shift+L subsequently should place us on all of the lists
# we found by pressing L, but in the reverse direction.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 1'",
     "     VISIBLE:  'Nesting level 1', cursor=0",
     "BRAILLE LINE:  '◦was a composer who was not square'",
     "     VISIBLE:  '◦was a composer who was not squa', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: '◦was a composer who was not square'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 2'",
     "     VISIBLE:  'Nesting level 2', cursor=0",
     "BRAILLE LINE:  '◦if your TYPE is circle'",
     "     VISIBLE:  '◦if your TYPE is circle', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: '◦if your TYPE is circle'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 3'",
     "     VISIBLE:  'Nesting level 3', cursor=0",
     "BRAILLE LINE:  '▪each sublevel'",
     "     VISIBLE:  '▪each sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 3'",
     "SPEECH OUTPUT: '▪each sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 2'",
     "     VISIBLE:  'Nesting level 2', cursor=0",
     "BRAILLE LINE:  '▪look for the bullet on'",
     "     VISIBLE:  '▪look for the bullet on', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: '▪look for the bullet on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  'Nesting level 1'",
     "     VISIBLE:  'Nesting level 1', cursor=0",
     "BRAILLE LINE:  '◦first sublevel'",
     "     VISIBLE:  '◦first sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: '◦first sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 2 items'",
     "     VISIBLE:  'List with 2 items', cursor=0",
     "BRAILLE LINE:  '•listing item'",
     "     VISIBLE:  '•listing item', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '•listing item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 6 items'",
     "     VISIBLE:  'List with 6 items', cursor=0",
     "BRAILLE LINE:  'VI.And use roman numerals,'",
     "     VISIBLE:  'VI.And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: 'List with 6 items'",
     "SPEECH OUTPUT: 'VI.And use roman numerals,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "shift + l", 
    ["BRAILLE LINE:  'List with 4 items'",
     "     VISIBLE:  'List with 4 items', cursor=0",
     "BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: 'List with 4 items'",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l", 1000))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
