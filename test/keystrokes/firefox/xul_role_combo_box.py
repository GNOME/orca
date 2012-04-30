#!/usr/bin/python

"""Test of combo box output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "Edit" menu and Up Arrow to Preferences, then press Return.
#
sequence.append(KeyComboAction("<Alt>e"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("", None))

sequence.append(PauseAction(3000))

########################################################################
# Press Tab to move to the "When Minefield starts" combo box.  This combo
# box is contained in a scroll pane called Main (which didn't used to
# have focus) in a panel called "Startup".  The currently selected item
# in the combo box is "Show a blank page".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show a blan', cursor=22",
     "SPEECH OUTPUT: 'General scroll pane Startup panel When " + utils.firefoxAppNames + " starts: Show a blank page combo box'"]))

########################################################################
# Now that focus is on the combo box, arrow down to "Show my windows
# and tabs from last time".
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show my windows and tabs from last time Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show my win', cursor=22",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

########################################################################
# Down arrow again to "Show my home page".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show my home page Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show my hom', cursor=22",
     "SPEECH OUTPUT: 'Show my home page'"]))

########################################################################
# Up arrow back to "Show my windows and tabs from last time".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show my windows and tabs from last time Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show my win', cursor=22",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

########################################################################
# Up arrow back to "Show a blank page".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show a blan', cursor=22",
     "SPEECH OUTPUT: 'Show a blank page'"]))

########################################################################
# Now expand the combo box with Alt+Down Arrow.  [[]]].
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "Alt Down Arrow to expand combobox",
    ["BUG? - I don't think we're getting any events related to the combo box expanding. We aren't speaking or brailling anything.",
     ""]))

########################################################################
# Down arrow again to "Show my windows and tabs from last time".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in expanded combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo Show my windows and tabs from last time'",
     "     VISIBLE:  'Show my windows and tabs from la', cursor=1",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

########################################################################
# Up arrow back to "Show a blank page".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in expanded combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "SPEECH OUTPUT: 'Show a blank page'"]))

########################################################################
# Press Return to collapse the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to collapse combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show a blan', cursor=22",
     "SPEECH OUTPUT: '" + utils.firefoxAppNames + " application " + utils.firefoxAppNames + " Preferences frame General scroll pane Startup panel When " + utils.firefoxAppNames + " starts: Show a blank page combo box'"]))

########################################################################
# Now try first letter navigation.  All of the items begin with S.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("s"))
sequence.append(utils.AssertPresentationAction(
    "First letter navigation with s",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show my home page Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show my hom', cursor=22",
     "SPEECH OUTPUT: 'Show my home page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("s"))
sequence.append(utils.AssertPresentationAction(
    "First letter navigation with s",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show a blan', cursor=22",
     "SPEECH OUTPUT: 'Show a blank page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  [[]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BUG? - We claim this is 1 of 1.",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame General ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo'",
     "     VISIBLE:  'When " + utils.firefoxAppNames + " starts: Show a blan', cursor=22",
     "SPEECH OUTPUT: 'When " + utils.firefoxAppNames + " starts: combo box Show a blank page 1 of 1'"]))

########################################################################
# Press Shift+Tab to move back to the Main list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Tab to list item",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List General ListItem'",
     "     VISIBLE:  'General ListItem', cursor=1",
     "SPEECH OUTPUT: 'General'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
