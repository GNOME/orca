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
sequence.append(WaitForWindowActivate("",None))

sequence.append(PauseAction(3000))

########################################################################
# Press Right Arrow to get to the next list item and Left Arrow to
# get back. We'll do this because in Firefox 3.1 we are not getting the
# correct events until we Alt+Tab out of and then back into the window.
# This does not seem to be an issue for Firefox 3.0
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow in list",
    ["KNOWN ISSUE - Firefox 3.1 is not giving us anything here, but Firefox 3.0 is. If we have output, the bug is not present."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow in list",
    ["KNOWN ISSUE - Firefox 3.1 is not giving us anything here, but Firefox 3.0 is. If we have output, the bug is not present."]))

sequence.append(KeyComboAction("<Alt>Tab"))
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))
sequence.append(KeyComboAction("<Alt>Tab"))
sequence.append(WaitForWindowActivate(utils.firefoxAppNames + " Preferences", None))

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
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo'",
     "     VISIBLE:  'Show a blank page Combo', cursor=1",
     "SPEECH OUTPUT: 'Main scroll pane Startup panel'",
     "SPEECH OUTPUT: 'When " + utils.firefoxAppNames + " starts: Show a blank page combo box'"]))

########################################################################
# Now that focus is on the combo box, arrow down to "Show my windows
# and tabs from last time".
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow my windows and tabs from last timeWhen " + utils.firefoxAppNames + " starts:  Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow my windows and tabs from last timeWhen " + utils.firefoxAppNames + " starts:  Show my windows and tabs from last time'",
     "     VISIBLE:  'Show my windows and tabs from la', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show a blank page'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

########################################################################
# Down arrow again to "Show my home page".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow my home pageWhen " + utils.firefoxAppNames + " starts:  Show my home page'",
     "     VISIBLE:  'Show my home page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show my home page'"]))

########################################################################
# Up arrow back to "Show my windows and tabs from last time".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow my windows and tabs from last timeWhen " + utils.firefoxAppNames + " starts:  Show my windows and tabs from last time'",
     "     VISIBLE:  'Show my windows and tabs from la', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

########################################################################
# Up arrow back to "Show a blank page".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow a blank pageWhen " + utils.firefoxAppNames + " starts:  Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "SPEECH OUTPUT: ''",
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
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow a blank pageWhen " + utils.firefoxAppNames + " starts:  Show my windows and tabs from last time'",
     "     VISIBLE:  'Show my windows and tabs from la', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

########################################################################
# Up arrow back to "Show a blank page".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in expanded combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow a blank pageWhen " + utils.firefoxAppNames + " starts:  Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show a blank page'"]))

########################################################################
# Press Return to collapse the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to collapse combobox",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel When " + utils.firefoxAppNames + " starts: Show a blank page Combo'",
     "     VISIBLE:  'Show a blank page Combo', cursor=1",
     "SPEECH OUTPUT: '" + utils.firefoxAppNames + " application " + utils.firefoxAppNames + " Preferences frame Main scroll pane Startup panel'",
     "SPEECH OUTPUT: 'When " + utils.firefoxAppNames + " starts: Show a blank page combo box'"]))

########################################################################
# Now try first letter navigation.  All of the items begin with S.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("s"))
sequence.append(utils.AssertPresentationAction(
    "First letter navigation with s",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow my home pageWhen " + utils.firefoxAppNames + " starts:  Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow my home pageWhen " + utils.firefoxAppNames + " starts:  Show my home page'",
     "     VISIBLE:  'Show my home page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show a blank page'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show my home page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("s"))
sequence.append(utils.AssertPresentationAction(
    "First letter navigation with s",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow a blank pageWhen " + utils.firefoxAppNames + " starts:  Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Show a blank page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  [[]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BUG? -  Techically the parent of the focused menu item (what combo boxes contain) is a menu, but in this case we presumably want to indicate that the focused item is a combo box.",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame Main ScrollPane Startup Panel  ComboShow a blank pageWhen " + utils.firefoxAppNames + " starts:  Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "SPEECH OUTPUT: 'Show a blank page menu'",
     "SPEECH OUTPUT: 'Show a blank page'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'item 1 of 1'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Press Shift+Tab to move back to the Main list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Tab to list item",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxAppNames + " Preferences Frame List Main ListItem'",
     "     VISIBLE:  'Main ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Main'"]))

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
