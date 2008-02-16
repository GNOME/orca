#!/usr/bin/python

"""Test of menu bar output of Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# [[[BUG: Sometimes menus on the menu bar in Firefox are claiming to be
# menu items. See https://bugzilla.mozilla.org/show_bug.cgi?id=396799]]]
#

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(utils.AssertPresentationAction(
    "File menu",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar New Window(Control N)'",
     "     VISIBLE:  'New Window(Control N)', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'File menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'New Window Control N'"]))

########################################################################
# Press Right Arrow to move forward menu by menu
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow on menu bar",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Edit Menu'",
     "     VISIBLE:  'Edit Menu', cursor=1",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Undo grayed(Control Z)'",
     "     VISIBLE:  'Undo grayed(Control Z)', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Edit menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Undo grayed Control Z'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow on menu bar",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar AutoComplete Location  $l'",
     "     VISIBLE:  'View Menu', cursor=1",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Toolbars Menu'",
     "     VISIBLE:  'Toolbars Menu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Toolbars menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow on menu bar",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar View Menu <x> Navigation Toolbar CheckItem'",
     "     VISIBLE:  '<x> Navigation Toolbar CheckItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Navigation Toolbar check item checked'"]))

########################################################################
# Press Left Arrow to move backward menu by menu
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow on menu bar",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar AutoComplete Location  $l'",
     "     VISIBLE:  'Location  $l', cursor=10",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Toolbars Menu'",
     "     VISIBLE:  'Toolbars Menu', cursor=1",
     "SPEECH OUTPUT: 'Location autocomplete'",
     "SPEECH OUTPUT: 'Location text '",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Toolbars menu'",]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow on menu bar",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Edit Menu'",
     "     VISIBLE:  'Edit Menu', cursor=1",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Paste(Control V)'",
     "     VISIBLE:  'Paste(Control V)', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Edit menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Paste Control V'"]))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
