# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output with HTML lists in Firefox"""

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
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Welcome to a List of Lists heading level 1'",
     "SPEECH OUTPUT: 'Lists are not only fun to make, they are fun to use. They help us: 1. remember what the heck we are doing each day 2. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of priority, even if it is artificial 3. look really cool when we carry them around on yellow Post-Itstm. 4. and that other thing I keep forgetting. Your ordered lists can start at a strange number, like: VI. And use roman numerals, g. You might try using letters as well, H. Maybe you prefer Big Letters, ix. or small roman numerals • But discs belong to unordered lists 50. Though you can set the value in a list item! Unordered list: • listing item • first sublevel • look for the bullet on • each sublevel • they should all be different, except here. • second sublevel • or you can specify a square • if your TYPE is circle • or even a disc • Franz Liszt • was a composer who was not square • would have liked the Who • feeling listless • blah, blah, blah • whine, whine, whine'"]))

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
