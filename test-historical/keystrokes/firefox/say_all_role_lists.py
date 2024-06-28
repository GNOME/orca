#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Welcome to a List of Lists'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'Lists are not only fun to make, they are fun to use.'",
     "SPEECH OUTPUT: 'They help us:'",
     "SPEECH OUTPUT: 'List with 4 items'",
     "SPEECH OUTPUT: '1. remember what the heck we are doing each day'",
     "SPEECH OUTPUT: '2. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of priority, even if it is artificial'",
     "SPEECH OUTPUT: '3. look really cool when we carry them around on yellow Post-Itstm.'",
     "SPEECH OUTPUT: '4. and that other thing I keep forgetting.'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'Your ordered lists can start at a strange number, like:'",
     "SPEECH OUTPUT: 'List with 6 items'",
     "SPEECH OUTPUT: '6. And use roman numerals,'",
     "SPEECH OUTPUT: 'g. You might try using letters as well,'",
     "SPEECH OUTPUT: 'H. Maybe you prefer Big Letters,'",
     "SPEECH OUTPUT: '9. or small roman numerals'",
     "SPEECH OUTPUT: '• But discs belong to unordered lists'",
     "SPEECH OUTPUT: '50. Though you can set the value in a list item!'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'Unordered list:'",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '• listing item'",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '◦ first sublevel'",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '◾ look for the bullet on'",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '◾ each sublevel'",
     "SPEECH OUTPUT: '◾ they should all be different, except here.'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: '◾ second sublevel'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: '◾ or you can specify a square'",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '◦ if your TYPE is circle'",
     "SPEECH OUTPUT: '• or even a disc'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: '◾ Franz Liszt'",
     "SPEECH OUTPUT: 'List with 2 items'",
     "SPEECH OUTPUT: '◦ was a composer who was not square'",
     "SPEECH OUTPUT: '• would have liked the Who'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '◦ feeling listless'",
     "SPEECH OUTPUT: '◾ blah, blah, blah'",
     "SPEECH OUTPUT: '• whine, whine, whine'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
