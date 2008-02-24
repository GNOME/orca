# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of tree table output using Firefox.
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
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Show All Bookmarks...'",
     "     VISIBLE:  'Show All Bookmarks...', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show All Bookmarks…'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

########################################################################
# Press Down Arrow to get to the first item in the tree.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in tree table",
    ["BRAILLE LINE:  'Minefield Application Library Frame ScrollPane TreeTable Name ColumnHeader Bookmarks Menu   TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Menu   TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Name column header'",
     "SPEECH OUTPUT: 'Bookmarks Menu  '",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Library Frame ScrollPane TreeTable Name ColumnHeader Bookmarks Menu TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Menu TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: 'tree table'",
     "SPEECH OUTPUT: 'Name'",
     "SPEECH OUTPUT: 'cell'",
     "SPEECH OUTPUT: 'Bookmarks Menu'",
     "SPEECH OUTPUT: 'row 2 of 3'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Press Up Arrow to return to the previous item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in tree table",
    ["BRAILLE LINE:  'Minefield Application Library Frame ScrollPane TreeTable Name ColumnHeader Bookmarks Toolbar   TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Toolbar   TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmarks Toolbar  '"]))

########################################################################
# Press Alt F4 to close the window.
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
