# -*- coding: utf-8 -*-
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
# Press I to move among all of the items (sub items, sub sub items, 
# etc.) in the third list.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '◦first sublevel'",
     "     VISIBLE:  '◦first sublevel', cursor=1",
     "SPEECH OUTPUT: '◦first sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '▪look for the bullet on'",
     "     VISIBLE:  '▪look for the bullet on', cursor=1",
     "SPEECH OUTPUT: '▪look for the bullet on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '▪each sublevel'",
     "     VISIBLE:  '▪each sublevel', cursor=1",
     "SPEECH OUTPUT: '▪each sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '▪they should all be different, except here.'",
     "     VISIBLE:  '▪they should all be different, e', cursor=1",
     "SPEECH OUTPUT: '▪they should all be different, except here.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '▪second sublevel'",
     "     VISIBLE:  '▪second sublevel', cursor=1",
     "SPEECH OUTPUT: '▪second sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '▪or you can specify a square'",
     "     VISIBLE:  '▪or you can specify a square', cursor=1",
     "SPEECH OUTPUT: '▪or you can specify a square'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '◦if your TYPE is circle'",
     "     VISIBLE:  '◦if your TYPE is circle', cursor=1",
     "SPEECH OUTPUT: '◦if your TYPE is circle'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '•or even a disc'",
     "     VISIBLE:  '•or even a disc', cursor=1",
     "SPEECH OUTPUT: '•or even a disc'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '▪Franz Liszt'",
     "     VISIBLE:  '▪Franz Liszt', cursor=1",
     "SPEECH OUTPUT: '▪Franz Liszt'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '◦was a composer who was not square'",
     "     VISIBLE:  '◦was a composer who was not squa', cursor=1",
     "SPEECH OUTPUT: '◦was a composer who was not square'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '•would have liked the Who'",
     "     VISIBLE:  '•would have liked the Who', cursor=1",
     "SPEECH OUTPUT: '•would have liked the Who'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '◦feeling listless'",
     "     VISIBLE:  '◦feeling listless', cursor=1",
     "SPEECH OUTPUT: '◦feeling listless"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '▪blah, blah, blah'",
     "     VISIBLE:  '▪blah, blah, blah', cursor=1",
     "SPEECH OUTPUT: '▪blah, blah, blah'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in third list", 
    ["BRAILLE LINE:  '•whine, whine, whine'",
     "     VISIBLE:  '•whine, whine, whine', cursor=1",
     "SPEECH OUTPUT: '•whine, whine, whine'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i should wrap to top", 
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "i in first list", 
    ["BRAILLE LINE:  '2.arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of priority, even if it is artificial'",
     "     VISIBLE:  '2.arrange long and arbitrary lin', cursor=1",
     "SPEECH OUTPUT: '2.arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of priority, even if it is artificial'"]))

########################################################################
# Now reverse our direction, but just for a few items.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(utils.AssertPresentationAction(
    "shift + i in first list", 
    ["BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(utils.AssertPresentationAction(
    "shift + i should wrap to bottom", 
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  '•whine, whine, whine'",
     "     VISIBLE:  '•whine, whine, whine', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: '•whine, whine, whine'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(utils.AssertPresentationAction(
    "shift + i in third list", 
    ["BRAILLE LINE:  '▪blah, blah, blah'",
     "     VISIBLE:  '▪blah, blah, blah', cursor=1",
     "SPEECH OUTPUT: '▪blah, blah, blah'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>i"))
sequence.append(utils.AssertPresentationAction(
    "shift + i in third list", 
    ["BRAILLE LINE:  '◦feeling listless'",
     "     VISIBLE:  '◦feeling listless', cursor=1",
     "SPEECH OUTPUT: '◦feeling listless'"]))

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
