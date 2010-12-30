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
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "Bookmarks" menu, Down Arrow to Show All Bookmarks, then 
# press Return.
#
sequence.append(PauseAction(3000))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>b"))
sequence.append(utils.AssertPresentationAction(
    "Bookmarks menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Application MenuBar Bookmark This Page\(Control D\)'",
     "     VISIBLE:  'Bookmark This Page(Control D)', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks menu Bookmark This Page Control D'"]))

# Firefox 3.5 introduces a shortcut (Control Shift O) that was not present
# in earlier versions.
#
sequence.append(PauseAction(3000))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in Bookmarks menu",
   ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Application MenuBar Show All Bookmarks...(\(Control Shift O\)|)'",
     "     VISIBLE:  'Show All Bookmarks...(\(Control Sh|)', cursor=1",
     "SPEECH OUTPUT: 'Show All Bookmarks…( Control Shift O|)'"]))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

########################################################################
# Press Down Arrow to get to the first item in the tree.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in tree table",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame ScrollPane TreeTable Location ColumnHeader Bookmarks Menu ListItem TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Menu ListItem TREE LEV', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Menu'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame ScrollPane TreeTable Location ColumnHeader Bookmarks Menu ListItem TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Menu ListItem TREE LEV', cursor=1",
     "SPEECH OUTPUT: 'list item Bookmarks Menu 2 of 3 tree level 1'"]))

########################################################################
# Press Up Arrow to return to the previous item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in tree table",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame ScrollPane TreeTable Tags ColumnHeader Bookmarks Toolbar ListItem TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Toolbar ListItem TREE ', cursor=1",
     "SPEECH OUTPUT: 'Bookmarks Toolbar'"]))

########################################################################
# Press Alt F4 to close the window.
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
