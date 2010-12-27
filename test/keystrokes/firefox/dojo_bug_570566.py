# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of fix for bug 570566 (Orca goes silent when navigating to
uneditable text from an ARIA widget) using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Editor Test" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the editor test demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "editor/test_Editor.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Editor Test", 
                              acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Extra loading time.
#
sequence.append(PauseAction(10000))

########################################################################
# Up Arrow to the heading above, and continue Up Arrowing to the top of
# the page.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BRAILLE LINE:  'ToolBar'",
     "     VISIBLE:  'ToolBar', cursor=1",
     "SPEECH OUTPUT: 'tool bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BRAILLE LINE:  'No plugins, initially empty h2'",
     "     VISIBLE:  'No plugins, initially empty h2', cursor=1",
     "SPEECH OUTPUT: 'No plugins, initially empty heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    ["BRAILLE LINE:  'Editor + Plugins Test h1'",
     "     VISIBLE:  'Editor + Plugins Test h1', cursor=1",
     "SPEECH OUTPUT: 'Editor + Plugins Test heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow", 
    ["BUG? - The braille is not ideal, nor does it jive with the speech.",
     "BRAILLE LINE:  '<x> CheckBox<x> CheckBox<x> CheckBox<x> CheckBox<x> CheckBox'",
     "     VISIBLE:  'CheckBox<x> CheckBox<x> CheckBox', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow", 
    ["BRAILLE LINE:  'Focus:<x> CheckBox Value:<x> CheckBox Change:<x> CheckBox Blur:<x> CheckBox Disabled:<x> CheckBox'",
     "     VISIBLE:  'Focus:<x> CheckBox Value:<x> Che', cursor=1",
     "SPEECH OUTPUT: 'Focus: check box checked grayed  Value: check box checked grayed  Change: check box checked grayed  Blur: check box checked grayed  Disabled: check box checked grayed ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up Arrow", 
    ["BRAILLE LINE:  'Automated Test - all check boxes should be checked'",
     "     VISIBLE:  'Automated Test - all check boxes', cursor=1",
     "SPEECH OUTPUT: 'Automated Test - all check boxes should be checked'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
