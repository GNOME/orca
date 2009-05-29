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
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "File" menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(utils.AssertPresentationAction(
    "File menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar New Window\(Control N\)'",
     "     VISIBLE:  'New Window(Control N)', cursor=1",
     "SPEECH OUTPUT: 'File menu'",
     "SPEECH OUTPUT: 'New Window Control N'"]))

########################################################################
# Press Right Arrow to move forward menu by menu
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow on menu bar",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Edit Menu'",
     "     VISIBLE:  'Edit Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Undo( grayed|)\(Control Z\)'",
     "     VISIBLE:  'Undo( grayed|)\(Control Z\)', cursor=1",
     "SPEECH OUTPUT: 'Edit menu'",
     "SPEECH OUTPUT: 'Undo( grayed|) Control Z'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow on menu bar",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar View Menu'",
     "     VISIBLE:  'View Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Toolbars Menu'",
     "     VISIBLE:  'Toolbars Menu', cursor=1",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Toolbars menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow on menu bar",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar View Menu <x> Navigation Toolbar CheckItem'",
     "     VISIBLE:  '<x> Navigation Toolbar CheckItem', cursor=1",
     "SPEECH OUTPUT: 'Navigation Toolbar check item checked'"]))

########################################################################
# Press Left Arrow to move backward menu by menu
#

# The location bar has different names. Where the cursor is will depend
# on the length of the name.
#
cursorPosition = utils.firefoxLocationBarNames
for name in cursorPosition[1:-1].split("|"):
    cursorPosition = cursorPosition.replace(name, "%s" % (len(name) + 2))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow on menu bar",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar AutoComplete " + utils.firefoxLocationBarNames + "  \$l'",
     "     VISIBLE:  '" + utils.firefoxLocationBarNames + "  \$l', cursor=%s" % cursorPosition,
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Toolbars Menu'",
     "     VISIBLE:  'Toolbars Menu', cursor=1",
     "SPEECH OUTPUT: '" + utils.firefoxLocationBarNames + " text '",
     "SPEECH OUTPUT: 'View menu Toolbars menu'",]))

# This seems to vary depending on whether or not something is in the
# clipboard. Therefore, we'll check for either.
#
menuItem = "(Paste|Select All|Undo)"
itemShortcut = "(V|A|Z)"

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow on menu bar",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Edit Menu'",
     "     VISIBLE:  'Edit Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar " + menuItem + "\(Control " + itemShortcut + "\)'",
     "     VISIBLE:  '" + menuItem + "\(Control " + itemShortcut + "\)', cursor=1",
     "SPEECH OUTPUT: 'Edit menu'",
     "SPEECH OUTPUT: '" + menuItem + " Control " + itemShortcut + "'"]))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
