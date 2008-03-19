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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "Bookmarks" menu, Down Arrow to Show All Bookmarks, then 
# press Return.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>b"))
sequence.append(utils.AssertPresentationAction(
    "Bookmarks menu",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Bookmarks Menu'",
     "     VISIBLE:  'Bookmarks Menu', cursor=1",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Bookmark This Page(Control D)'",
     "     VISIBLE:  'Bookmark This Page(Control D)', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmarks menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmark This Page Control D'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in Bookmarks menu",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Organize Bookmarks'",
     "     VISIBLE:  'Organize Bookmarks', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Organize Bookmarks'"]))

sequence.append(KeyComboAction("Return"))

########################################################################
# Press Shift+F10 to bring up a context menu then Down Arrow once to
# get to "New Bookmark..." and press Return.
#
sequence.append(KeyComboAction("<Shift>F10"))
sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 1000))
sequence.append(utils.AssertPresentationAction(
    "Return for a new bookmark",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog'",
     "     VISIBLE:  'Add Bookmark Dialog', cursor=1",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Add Bookmark'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Name: text '"]))

########################################################################
# Focus will be in the Name single-line entry.  Type "this is a test"
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("this is a test"))
sequence.append(utils.AssertPresentationAction(
    "Type 'this is a test'",
    [     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog t $l'",
     "     VISIBLE:  't $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog t $l'",
     "     VISIBLE:  't $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog th $l'",
     "     VISIBLE:  'th $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog th $l'",
     "     VISIBLE:  'th $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog thi $l'",
     "     VISIBLE:  'thi $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog thi $l'",
     "     VISIBLE:  'thi $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this $l'",
     "     VISIBLE:  'this $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this $l'",
     "     VISIBLE:  'this $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this  $l'",
     "     VISIBLE:  'this  $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this  $l'",
     "     VISIBLE:  'this  $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this i $l'",
     "     VISIBLE:  'this i $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this i $l'",
     "     VISIBLE:  'this i $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is $l'",
     "     VISIBLE:  'this is $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is $l'",
     "     VISIBLE:  'this is $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is  $l'",
     "     VISIBLE:  'this is  $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is  $l'",
     "     VISIBLE:  'this is  $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a $l'",
     "     VISIBLE:  'this is a $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a $l'",
     "     VISIBLE:  'this is a $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a  $l'",
     "     VISIBLE:  'this is a  $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a  $l'",
     "     VISIBLE:  'this is a  $l', cursor=11",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a t $l'",
     "     VISIBLE:  'this is a t $l', cursor=11",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a t $l'",
     "     VISIBLE:  'this is a t $l', cursor=12",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a te $l'",
     "     VISIBLE:  'this is a te $l', cursor=12",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a te $l'",
     "     VISIBLE:  'this is a te $l', cursor=13",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a tes $l'",
     "     VISIBLE:  'this is a tes $l', cursor=13",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a tes $l'",
     "     VISIBLE:  'this is a tes $l', cursor=14",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a test $l'",
     "     VISIBLE:  'this is a test $l', cursor=14",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a test $l'",
     "     VISIBLE:  'this is a test $l', cursor=15"]))

########################################################################
# Backspace 5 times (thus removing "<space>test" from the right)
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a test $l'",
     "     VISIBLE:  'this is a test $l', cursor=15",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a test $l'",
     "     VISIBLE:  'this is a test $l', cursor=14",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a tes $l'",
     "     VISIBLE:  'this is a tes $l', cursor=14",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a tes $l'",
     "     VISIBLE:  'this is a tes $l', cursor=13",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a te $l'",
     "     VISIBLE:  'this is a te $l', cursor=13",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a te $l'",
     "     VISIBLE:  'this is a te $l', cursor=12",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a t $l'",
     "     VISIBLE:  'this is a t $l', cursor=12",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a t $l'",
     "     VISIBLE:  'this is a t $l', cursor=11",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a  $l'",
     "     VISIBLE:  'this is a  $l', cursor=11",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a  $l'",
     "     VISIBLE:  'this is a  $l', cursor=10",
     "SPEECH OUTPUT: ' '"]))

########################################################################
# Control Backspace 3 times thus removing "this is a" word by word from
# the right.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Control Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a $l'",
     "     VISIBLE:  'this is a $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is a $l'",
     "     VISIBLE:  'this is a $l', cursor=9",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Control Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is  $l'",
     "     VISIBLE:  'this is  $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this is  $l'",
     "     VISIBLE:  'this is  $l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Control Backspace",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this  $l'",
     "     VISIBLE:  'this  $l', cursor=1",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this  $l'",
     "     VISIBLE:  'this  $l', cursor=1",
     "SPEECH OUTPUT: 'this '"]))

########################################################################
# Type "so is this"
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("so is this"))
sequence.append(utils.AssertPresentationAction(
    "Type 'so is this'",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog s $l'",
     "     VISIBLE:  's $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog s $l'",
     "     VISIBLE:  's $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so $l'",
     "     VISIBLE:  'so $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so $l'",
     "     VISIBLE:  'so $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so  $l'",
     "     VISIBLE:  'so  $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so  $l'",
     "     VISIBLE:  'so  $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so i $l'",
     "     VISIBLE:  'so i $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so i $l'",
     "     VISIBLE:  'so i $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is $l'",
     "     VISIBLE:  'so is $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is $l'",
     "     VISIBLE:  'so is $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is  $l'",
     "     VISIBLE:  'so is  $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is  $l'",
     "     VISIBLE:  'so is  $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is t $l'",
     "     VISIBLE:  'so is t $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is t $l'",
     "     VISIBLE:  'so is t $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is th $l'",
     "     VISIBLE:  'so is th $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is th $l'",
     "     VISIBLE:  'so is th $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is thi $l'",
     "     VISIBLE:  'so is thi $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is thi $l'",
     "     VISIBLE:  'so is thi $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=11"]))

########################################################################
# Press Left Arrow 4 times to get to the beginning of "this"
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=10",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=9",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=8",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
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
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=4",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Control Left",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=1",
     "SPEECH OUTPUT: 'so '"]))

########################################################################
# Press Control Delete twice to get rid of "so is".  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Delete"))
sequence.append(utils.AssertPresentationAction(
    "Control Delete",
    ["BUG? - We are speaking the new caret location -- we land on a space -- rather than the word that was just deleted.",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog so is this $l'",
     "     VISIBLE:  'so is this $l', cursor=3",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Delete"))
sequence.append(utils.AssertPresentationAction(
    "Control Delete",
    ["BUG? - We are speaking the new caret location -- we land on a space -- rather than the word that was just deleted.",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  is this $l'",
     "     VISIBLE:  ' is this $l', cursor=4",
     "SPEECH OUTPUT: ' '"]))

########################################################################
# Press Delete 5 times to delete "<space>this".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  this $l'",
     "     VISIBLE:  ' this $l', cursor=2",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog this $l'",
     "     VISIBLE:  'this $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog his $l'",
     "     VISIBLE:  'his $l', cursor=2",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog is $l'",
     "     VISIBLE:  'is $l', cursor=2",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete", 500))
sequence.append(utils.AssertPresentationAction(
    "Delete",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog s $l'",
     "     VISIBLE:  's $l', cursor=2",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Press Tab to get to the Location entry.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Location",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Location: text '"]))

########################################################################
# Press Tab to get to the Keyword entry.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Keyword",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Keyword: text '"]))

########################################################################
# Press Tab to get to the Description entry.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Description",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Description: text '"]))

########################################################################
# Type "Here is the first line."  Press Return.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("Here is the first line."))
sequence.append(utils.AssertPresentationAction(
    "Type 'Here is the first line.'",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog H $l'",
     "     VISIBLE:  'H $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog H $l'",
     "     VISIBLE:  'H $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog H $l'",
     "     VISIBLE:  'H $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog He $l'",
     "     VISIBLE:  'He $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog He $l'",
     "     VISIBLE:  'He $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Her $l'",
     "     VISIBLE:  'Her $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Her $l'",
     "     VISIBLE:  'Her $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here $l'",
     "     VISIBLE:  'Here $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here $l'",
     "     VISIBLE:  'Here $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here  $l'",
     "     VISIBLE:  'Here  $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here  $l'",
     "     VISIBLE:  'Here  $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here i $l'",
     "     VISIBLE:  'Here i $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here i $l'",
     "     VISIBLE:  'Here i $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is $l'",
     "     VISIBLE:  'Here is $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is $l'",
     "     VISIBLE:  'Here is $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is  $l'",
     "     VISIBLE:  'Here is  $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is  $l'",
     "     VISIBLE:  'Here is  $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is t $l'",
     "     VISIBLE:  'Here is t $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is t $l'",
     "     VISIBLE:  'Here is t $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is th $l'",
     "     VISIBLE:  'Here is th $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is th $l'",
     "     VISIBLE:  'Here is th $l', cursor=11",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the $l'",
     "     VISIBLE:  'Here is the $l', cursor=11",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the $l'",
     "     VISIBLE:  'Here is the $l', cursor=12",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the  $l'",
     "     VISIBLE:  'Here is the  $l', cursor=12",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the  $l'",
     "     VISIBLE:  'Here is the  $l', cursor=13",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the f $l'",
     "     VISIBLE:  'Here is the f $l', cursor=13",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the f $l'",
     "     VISIBLE:  'Here is the f $l', cursor=14",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the fi $l'",
     "     VISIBLE:  'Here is the fi $l', cursor=14",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the fi $l'",
     "     VISIBLE:  'Here is the fi $l', cursor=15",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the fir $l'",
     "     VISIBLE:  'Here is the fir $l', cursor=15",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the fir $l'",
     "     VISIBLE:  'Here is the fir $l', cursor=16",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the firs $l'",
     "     VISIBLE:  'Here is the firs $l', cursor=16",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the firs $l'",
     "     VISIBLE:  'Here is the firs $l', cursor=17",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first $l'",
     "     VISIBLE:  'Here is the first $l', cursor=17",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first $l'",
     "     VISIBLE:  'Here is the first $l', cursor=18",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first  $l'",
     "     VISIBLE:  'Here is the first  $l', cursor=18",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first  $l'",
     "     VISIBLE:  'Here is the first  $l', cursor=19",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first l $l'",
     "     VISIBLE:  'Here is the first l $l', cursor=19",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first l $l'",
     "     VISIBLE:  'Here is the first l $l', cursor=20",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first li $l'",
     "     VISIBLE:  'Here is the first li $l', cursor=20",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first li $l'",
     "     VISIBLE:  'Here is the first li $l', cursor=21",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first lin $l'",
     "     VISIBLE:  'Here is the first lin $l', cursor=21",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first lin $l'",
     "     VISIBLE:  'Here is the first lin $l', cursor=22",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first line $l'",
     "     VISIBLE:  'Here is the first line $l', cursor=22",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first line $l'",
     "     VISIBLE:  'Here is the first line $l', cursor=23",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first line. $l'",
     "     VISIBLE:  'Here is the first line. $l', cursor=23",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first line. $l'",
     "     VISIBLE:  'Here is the first line. $l', cursor=24"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return for new line'",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog  $l'",
     "     VISIBLE:  ' $l', cursor=1"]))

########################################################################
# Type "Here is the second line."
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("Here is the second line."))
sequence.append(utils.AssertPresentationAction(
    "Type 'Here is the second line.'",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog H $l'",
     "     VISIBLE:  'H $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog H $l'",
     "     VISIBLE:  'H $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog He $l'",
     "     VISIBLE:  'He $l', cursor=2",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog He $l'",
     "     VISIBLE:  'He $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Her $l'",
     "     VISIBLE:  'Her $l', cursor=3",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Her $l'",
     "     VISIBLE:  'Her $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here $l'",
     "     VISIBLE:  'Here $l', cursor=4",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here $l'",
     "     VISIBLE:  'Here $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here  $l'",
     "     VISIBLE:  'Here  $l', cursor=5",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here  $l'",
     "     VISIBLE:  'Here  $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here i $l'",
     "     VISIBLE:  'Here i $l', cursor=6",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here i $l'",
     "     VISIBLE:  'Here i $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is $l'",
     "     VISIBLE:  'Here is $l', cursor=7",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is $l'",
     "     VISIBLE:  'Here is $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is  $l'",
     "     VISIBLE:  'Here is  $l', cursor=8",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is  $l'",
     "     VISIBLE:  'Here is  $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is t $l'",
     "     VISIBLE:  'Here is t $l', cursor=9",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is t $l'",
     "     VISIBLE:  'Here is t $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is th $l'",
     "     VISIBLE:  'Here is th $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is th $l'",
     "     VISIBLE:  'Here is th $l', cursor=11",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the $l'",
     "     VISIBLE:  'Here is the $l', cursor=11",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the $l'",
     "     VISIBLE:  'Here is the $l', cursor=12",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the  $l'",
     "     VISIBLE:  'Here is the  $l', cursor=12",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the  $l'",
     "     VISIBLE:  'Here is the  $l', cursor=13",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the s $l'",
     "     VISIBLE:  'Here is the s $l', cursor=13",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the s $l'",
     "     VISIBLE:  'Here is the s $l', cursor=14",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the se $l'",
     "     VISIBLE:  'Here is the se $l', cursor=14",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the se $l'",
     "     VISIBLE:  'Here is the se $l', cursor=15",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the sec $l'",
     "     VISIBLE:  'Here is the sec $l', cursor=15",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the sec $l'",
     "     VISIBLE:  'Here is the sec $l', cursor=16",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the seco $l'",
     "     VISIBLE:  'Here is the seco $l', cursor=16",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the seco $l'",
     "     VISIBLE:  'Here is the seco $l', cursor=17",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the secon $l'",
     "     VISIBLE:  'Here is the secon $l', cursor=17",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the secon $l'",
     "     VISIBLE:  'Here is the secon $l', cursor=18",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second $l'",
     "     VISIBLE:  'Here is the second $l', cursor=18",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second $l'",
     "     VISIBLE:  'Here is the second $l', cursor=19",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second  $l'",
     "     VISIBLE:  'Here is the second  $l', cursor=19",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second  $l'",
     "     VISIBLE:  'Here is the second  $l', cursor=20",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second l $l'",
     "     VISIBLE:  'Here is the second l $l', cursor=20",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second l $l'",
     "     VISIBLE:  'Here is the second l $l', cursor=21",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second li $l'",
     "     VISIBLE:  'Here is the second li $l', cursor=21",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second li $l'",
     "     VISIBLE:  'Here is the second li $l', cursor=22",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second lin $l'",
     "     VISIBLE:  'Here is the second lin $l', cursor=22",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second lin $l'",
     "     VISIBLE:  'Here is the second lin $l', cursor=23",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line $l'",
     "     VISIBLE:  'Here is the second line $l', cursor=23",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line $l'",
     "     VISIBLE:  'Here is the second line $l', cursor=24",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line. $l'",
     "     VISIBLE:  'Here is the second line. $l', cursor=24",
     "BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line. $l'",
     "     VISIBLE:  'Here is the second line. $l', cursor=25"]))

########################################################################
# Press Up Arrow to read the first line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the first line. $l'",
     "     VISIBLE:  'Here is the first line. $l', cursor=24",
     "SPEECH OUTPUT: 'Here is the first line.'"]))

########################################################################
# Press Down Arrow to read the first line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow",
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line. $l'",
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
    ["BRAILLE LINE:  'Minefield Application Add Bookmark Dialog Here is the second line. $l'",
     "     VISIBLE:  'Here is the second line. $l', cursor=25",
     "SPEECH OUTPUT: 'Here is the first line.",
     "Here is the second line.'",
     "SPEECH OUTPUT: 'text'"]))

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
sequence.append(WaitForWindowActivate("Minefield",None))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
