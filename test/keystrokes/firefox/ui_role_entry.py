#!/usr/bin/python

"""Test of entry output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control><Shift>o"))


########################################################################
# Tab three times, then down arrow twice to Bookmarks Menu. (This is
# necessary to add a new item).  Then Press Alt+O for Organize and Return
# on "New Bookmark..."
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(KeyComboAction("Return"))

# This is to deal with a timing issue
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Shift>Tab"))

sequence.append(KeyComboAction("<Control>a"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(TypeAction("this is a test"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "1. Backspace",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is a tes $l'",
     "     VISIBLE:  'Name: this is a tes $l', cursor=20",
     "BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is a tes $l'",
     "     VISIBLE:  'Name: this is a tes $l', cursor=20",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "2. Backspace",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is a te $l'",
     "     VISIBLE:  'Name: this is a te $l', cursor=19",
     "BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is a te $l'",
     "     VISIBLE:  'Name: this is a te $l', cursor=19",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "3. Control Backspace",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is a  $l'",
     "     VISIBLE:  'Name: this is a  $l', cursor=17",
     "BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is a  $l'",
     "     VISIBLE:  'Name: this is a  $l', cursor=17",
     "SPEECH OUTPUT: 'te'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "4. Control Backspace",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is  $l'",
     "     VISIBLE:  'Name: this is  $l', cursor=15",
     "BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is  $l'",
     "     VISIBLE:  'Name: this is  $l', cursor=15",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Left",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is  $l'",
     "     VISIBLE:  'Name: this is  $l', cursor=14",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Left",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is  $l'",
     "     VISIBLE:  'Name: this is  $l', cursor=13",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Control Left",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this is  $l'",
     "     VISIBLE:  'Name: this is  $l', cursor=12",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete"))
sequence.append(utils.AssertPresentationAction(
    "8. Delete",
    ["BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this s  $l'",
     "     VISIBLE:  'Name: this s  $l', cursor=12",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "9. Basic Where Am I",
    ["KNOWN ISSUE: The mnemonic seems to have gone missing",
     "BRAILLE LINE:  'Firefox application New Bookmark dialog Name: this s  $l'",
     "     VISIBLE:  'Name: this s  $l', cursor=12",
     "SPEECH OUTPUT: 'Name: entry this s '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
