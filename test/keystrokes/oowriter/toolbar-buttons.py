#!/usr/bin/python

"""Test of Orca's presentation of Writer toolbar buttons."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# Start Writer
#
sequence.append(WaitForWindowActivate("Untitled[ ]*1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# Create a new document
#
sequence.append(KeyComboAction("<Control>n"))
sequence.append(PauseAction(3000))

######################################################################
# Press F6 until focus is on the Standard toolbar then Right arrow
# amongst the buttons. Also try to get a tooltip.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "F6 to menu bar",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane MenuBar'",
     "     VISIBLE:  'MenuBar', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "SPEECH OUTPUT: 'menu bar'",
     "SPEECH OUTPUT: 'File menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "F6 to Standard toolbar",
    ["BUG? - We should not be saying 'off' for this button and the buttons that follow.",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Standard ToolBar'",
     "     VISIBLE:  'Standard ToolBar', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Standard ToolBar New Button'",
     "     VISIBLE:  'New Button', cursor=1",
     "SPEECH OUTPUT: 'Standard tool bar'",
     "SPEECH OUTPUT: 'New off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Control F1 to show Tooltip.",
    ["BUG? - We're presenting nothing."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to Open button",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Standard ToolBar Open Button'",
     "     VISIBLE:  'Open Button', cursor=1",
     "SPEECH OUTPUT: 'Open off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to Save button",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Standard ToolBar Save Button'",
     "     VISIBLE:  'Save Button', cursor=1",
     "SPEECH OUTPUT: 'Save off grayed'"]))

######################################################################
# Press F6 to move to the Formatting Toolbar, then Right Arrow to
# Apply Style and press Return to activate it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(WaitForFocus("Styles and Formatting", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "F6 to Formatting Toolbar",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar'",
     "     VISIBLE:  'Formatting ToolBar', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar & y Styles and Formatting ToggleButton'",
     "     VISIBLE:  '& y Styles and Formatting Toggle', cursor=1",
     "SPEECH OUTPUT: 'Formatting tool bar'",
     "SPEECH OUTPUT: 'Styles and Formatting'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Apply Style", acc_role=pyatspi.ROLE_PANEL))
sequence.append(utils.AssertPresentationAction(
    "Right to Apply Style",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel'",
     "     VISIBLE:  'Apply Style Panel', cursor=1",
     "SPEECH OUTPUT: 'Apply Style panel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to activate Apply Style",
    ["BUG? - We're presenting nothing. Should we be indicating focus?"]))

######################################################################
# Down Arrow to change the selection without expanding the list first
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down in Apply Style (Collapsed)",
    ["BUG? - We're presenting nothing."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down in Apply Style (Collapsed)",
    ["BUG? - We're presenting nothing."]))

######################################################################
# Alt Down Arrow to expand the list. Then Down Arrow some.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "Alt Down to expand list",
    ["BUG? - We're presenting nothing. It might be nice to indicate the list is expanded."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down in Apply Style (Expanded)",
    ["BUG? - We're presenting nothing."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down in Apply Style (Expanded)",
    ["BUG? - We're presenting nothing."]))

######################################################################
# Up Arrow to restore the original style.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up in Apply Style (Expanded)",
    ["BUG? - We're presenting nothing."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up in Apply Style (Expanded)",
    ["BUG? - We're presenting nothing."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up in Apply Style (Expanded)",
    ["BUG? - We're presenting nothing."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up in Apply Style (Expanded)",
    ["BUG? - We're presenting nothing."]))

######################################################################
# Tab off of this item and then Shift+Tab back. That seems to get us
# speaking things again. Then Rinse and Repeat.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to activate Apply Style - Take 2",
    ["BUG? - We're presenting nothing. Should we be indicating focus?"]))

######################################################################
# Down Arrow to change the selection without expanding the list first
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down in Apply Style (Collapsed) - Take 2",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 1 \$l'",
     "     VISIBLE:  'Heading 1 $l', cursor=1",
    "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 1 \$l'",
     "     VISIBLE:  'Heading 1 $l', cursor=1",
    "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 1 \$l'",
     "     VISIBLE:  'Heading 1 $l', cursor=10",
     "SPEECH OUTPUT: 'Heading 1'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down in Apply Style (Collapsed) - Take 2",
    ["BUG? - We shouldn't be saying 'selected' here once, let alone twice. And we're not speaking the newly selected item. This bug appears quite a bit in this test, but I'm only marking it once.",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 2 \$l'",
     "     VISIBLE:  'Heading 2 $l', cursor=1",
    "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 2 \$l'",
     "     VISIBLE:  'Heading 2 $l', cursor=1",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'selected'"]))

######################################################################
# Alt Down Arrow to expand the list. Then Down Arrow some.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "Alt Down to expand list - Take 2",
    ["BUG? - We're presenting nothing. It might be nice to indicate the list is expanded."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down in Apply Style (Expanded) - Take 2",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 3 \$l'",
     "     VISIBLE:  'Heading 3 $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 3 \$l'",
     "     VISIBLE:  'Heading 3 $l', cursor=1",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down in Apply Style (Expanded) - Take 2",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Text body \$l'",
     "     VISIBLE:  'Text body $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Text body \$l'",
     "     VISIBLE:  'Text body $l', cursor=1",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'selected'"]))

######################################################################
# Up Arrow to restore the original style.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up in Apply Style (Expanded) - Take 2",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 3 \$l'",
     "     VISIBLE:  'Heading 3 $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 3 \$l'",
     "     VISIBLE:  'Heading 3 $l', cursor=1",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up in Apply Style (Expanded) - Take 2",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 2 \$l'",
     "     VISIBLE:  'Heading 2 $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 2 \$l'",
     "     VISIBLE:  'Heading 2 $l', cursor=1",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up in Apply Style (Expanded) - Take 2",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 1 \$l'",
     "     VISIBLE:  'Heading 1 $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Heading 1 \$l'",
     "     VISIBLE:  'Heading 1 $l', cursor=1",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up in Apply Style (Expanded) - Take 2",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Default \$l'",
     "     VISIBLE:  'Default $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Default \$l'",
     "     VISIBLE:  'Default $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Apply Style Panel Default \$l'",
     "     VISIBLE:  'Default $l', cursor=8",
     "SPEECH OUTPUT: 'Default'",
     "SPEECH OUTPUT: 'selected'"]))

######################################################################
# Press Alt Up to collapse the list. Then Tab to the Bold toggle/push
# button.
#
sequence.append(KeyComboAction("<Alt>Up"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Font Name", acc_role=pyatspi.ROLE_PANEL))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Font Size", acc_role=pyatspi.ROLE_PANEL))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Bold", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Tab to Bold",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Bold Button'",
     "     VISIBLE:  'Bold Button', cursor=1",
     "SPEECH OUTPUT: 'Bold off'"]))

######################################################################
# Press Return to toggle the state of the Bold toggle/push button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to toggle Bold on",
    ["BUG? - We're presenting nothing."]))

######################################################################
# Tab off of this item and then Shift+Tab back. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Italic", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Tab to Italic",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Italic Button'",
     "     VISIBLE:  'Italic Button', cursor=1",
     "SPEECH OUTPUT: 'Italic off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Bold", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab to Bold",
    ["BRAILLE LINE:  'soffice Application Untitled[ ]*2 - " + utils.getOOoName("Writer") + " Frame Untitled[ ]*2 - " + utils.getOOoName("Writer") + " RootPane Formatting ToolBar Bold Button'",
     "     VISIBLE:  'Bold Button', cursor=1",
     "SPEECH OUTPUT: 'Bold on'"]))

######################################################################
# Press Return to toggle the state of the Bold toggle/push button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to toggle Bold off",
    ["BUG? - We're presenting nothing."]))

######################################################################
# Press F6 to move focus back in the document.
#
sequence.append(KeyComboAction("F6"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# Close the new document
#
sequence.append(KeyComboAction("<Control>w"))
sequence.append(PauseAction(3000))

######################################################################
# Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# Wait before closing.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
