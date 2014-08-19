#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Welcome to a List of Lists'",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'Lists are not only fun to make, they are fun to use. They help us: 1.remember what the heck we are doing each day 2.arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of priority, even if it is artificial 3.look really cool when we carry them around on yellow Post-Itstm. 4.and that other thing I keep forgetting. Your ordered lists can start at a strange number, like: VI.And use roman numerals, g.You might try using letters as well, H.Maybe you prefer Big Letters, ix.or small roman numerals •But discs belong to unordered lists 50.Though you can set the value in a list item! Unordered list: •listing item ◦first sublevel ▪look for the bullet on ▪each sublevel ▪they should all be different, except here. ▪second sublevel or you can specify a square ◦if your TYPE is circle •or even a disc Franz Liszt ◦was a composer who was not square •would have liked the Who ◦feeling listless ▪blah, blah, blah •whine, whine, whine'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
