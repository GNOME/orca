# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of entry output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "Bookmarks" menu, Down Arrow to Organize Bookmarks, then 
# press Return.
#
sequence.append(KeyComboAction("<Alt>b"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("", None))
sequence.append(PauseAction(3000))

########################################################################
# Tab three times, then down arrow twice to Bookmarks Menu. (This is
# necessary to add a new item).  Then Press Alt+O for Organize and Return
# on "New Bookmark..."
#
sequence.append(KeyComboAction("Tab", 1000))
sequence.append(KeyComboAction("Tab", 1000))
sequence.append(KeyComboAction("Tab", 1000))
sequence.append(KeyComboAction("Down", 1000))
sequence.append(KeyComboAction("Down", 1000))
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(KeyComboAction("Return", 1000))
sequence.append(WaitForWindowActivate("", None))
sequence.append(PauseAction(3000))

# The dialog might be called Add Bookmark or it might be called New
# Bookmark. Depends on the verison of Firefox being used/tested.
#
dialogName = "(Add Bookmark|New Bookmark)"

# Depending on the version, there may also be text present in the entry
# So we'll delete it for good meausre.
#
sequence.append(KeyComboAction("<Control>a"))
sequence.append(KeyComboAction("BackSpace"))

########################################################################
# Focus will be in the Name single-line entry.  Type "this is a test"
#
sequence.append(TypeAction("this is a test"))

########################################################################
# Backspace 5 times (thus removing "<space>test" from the right)
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BUG? - Braille is not updating correctly - it's off by one character. This is true for the next four assertions as well.",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this is a test \$l'",
     "     VISIBLE:  'this is a test $l', cursor=15",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this is a tes \$l'",
     "     VISIBLE:  'this is a tes $l', cursor=14",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this is a te \$l'",
     "     VISIBLE:  'this is a te $l', cursor=13",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this is a t \$l'",
     "     VISIBLE:  'this is a t $l', cursor=12",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this is a  \$l'",
     "     VISIBLE:  'this is a  $l', cursor=11",
     "SPEECH OUTPUT: 'space'"]))

########################################################################
# Control Backspace 3 times thus removing "this is a" word by word from
# the right.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Control Backspace",
    ["BUG? - Braille is not updating correctly - it's off by one word. This is true for the next two assertions as well.",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this is a \$l'",
     "     VISIBLE:  'this is a $l', cursor=9",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Control Backspace",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this is  \$l'",
     "     VISIBLE:  'this is  $l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Control Backspace",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this  \$l'",
     "     VISIBLE:  'this  $l', cursor=1",
     "SPEECH OUTPUT: 'this '"]))

########################################################################
# Due to a bug, we'll stop getting caret-moved events if we don't move
# focus out of and back into this entry. Therefore, Tab to the next
# entry, Shift+Tab back, and type "so is this"
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(TypeAction("so is this"))

########################################################################
# Press Left Arrow 4 times to get to the beginning of "this"
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog so is this \$l'",
     "     VISIBLE:  'so is this $l', cursor=10",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog so is this \$l'",
     "     VISIBLE:  'so is this $l', cursor=9",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog so is this \$l'",
     "     VISIBLE:  'so is this $l', cursor=8",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog so is this \$l'",
     "     VISIBLE:  'so is this $l', cursor=7",
     "SPEECH OUTPUT: 't'"]))

########################################################################
# Press Control Left Arrow twice to get to the beginning of the 
# line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Control Left",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog so is this \$l'",
     "     VISIBLE:  'so is this $l', cursor=4",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Control Left",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog so is this \$l'",
     "     VISIBLE:  'so is this $l', cursor=1",
     "SPEECH OUTPUT: 'so '"]))

########################################################################
# Press Control Delete twice to get rid of "so is".  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Delete"))
sequence.append(utils.AssertPresentationAction(
    "Control Delete",
    ["BUG? - We are speaking the new caret location -- we land on a space -- rather than the word that was just deleted. This is true for the next assertion as well.",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog so is this \$l'",
     "     VISIBLE:  'so is this $l', cursor=3",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Delete"))
sequence.append(utils.AssertPresentationAction(
    "Control Delete",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog  is this \$l'",
     "     VISIBLE:  ' is this $l', cursor=4",
     "SPEECH OUTPUT: 'space'"]))

########################################################################
# Press Delete 5 times to delete "<space>this".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BUG? - Braille is not updating correctly - it's off by one character. This is true for the next three assertions as well.",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog  this \$l'",
     "     VISIBLE:  ' this $l', cursor=2",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog this \$l'",
     "     VISIBLE:  'this $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog his \$l'",
     "     VISIBLE:  'his $l', cursor=2",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog is \$l'",
     "     VISIBLE:  'is $l', cursor=2",
     "SPEECH OUTPUT: 's'"]))

########################################################################
# Press Alt+D times to get to the Description Entry.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>d"))
sequence.append(utils.AssertPresentationAction(
    "Alt+D to Description",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog  \$l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Description: text '"]))

########################################################################
# Type "Here is the first line."  Press Return.  
#
sequence.append(TypeAction("Here is the first line."))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return for new line'",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog  \$l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog  \$l'",
     "     VISIBLE:  ' $l', cursor=1"]))

########################################################################
# Type "Here is the second line."
#
sequence.append(TypeAction("Here is the second line."))

########################################################################
# Press Up Arrow to read the first line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog Here is the first line. \$l'",
     "     VISIBLE:  'Here is the first line. $l', cursor=24",
     "SPEECH OUTPUT: 'Here is the first line.'"]))

########################################################################
# Press Down Arrow to read the first line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog Here is the second line. \$l'",
     "     VISIBLE:  'Here is the second line. $l', cursor=25",
     "SPEECH OUTPUT: 'Here is the second line.'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + dialogName + " Dialog Here is the second line. \$l'",
     "     VISIBLE:  'Here is the second line. $l', cursor=25",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Here is the second line.",
     "'",
     "SPEECH OUTPUT: ''"]))

########################################################
# Press Escape to dismiss the dialog.  Focus should return to the
# Places Organizer.
#
sequence.append(KeyComboAction("Escape"))

########################################################################
# Now that the Places Manager is back to its pre-explored state,
# press Alt F4 to close it.
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Wait for the focus to be back on the blank Firefox window.
#
sequence.append(WaitForWindowActivate("",None))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
