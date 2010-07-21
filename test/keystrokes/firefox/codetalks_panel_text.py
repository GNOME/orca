# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of presentation of Codetalk's panel text using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://codetalks.org/source/widgets/tabpanel/tabpanel.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Down Arrow from the page tab to the panel text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["BRAILLE LINE:  'Tab Zero Page'",
     "     VISIBLE:  'Tab Zero Page', cursor=1",
     "SPEECH OUTPUT: 'Tab Zero scroll pane'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["BRAILLE LINE:  'This example requires Firefox 3 or later to work with screen readers -- it uses ARIA properties without'",
     "     VISIBLE:  'This example requires Firefox 3 ', cursor=1",
     "SPEECH OUTPUT: 'This example requires Firefox 3 or later to work with screen readers -- it uses ARIA properties without'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow", 
    ["BRAILLE LINE:  'namespaces, which is now the correct markup.'",
     "     VISIBLE:  'namespaces, which is now the cor', cursor=1",
     "SPEECH OUTPUT: 'namespaces, which is now the correct markup.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow", 
    ["BRAILLE LINE:  'Use tab key to reach the tab. Once a tab has focus use:'",
     "     VISIBLE:  'Use tab key to reach the tab. On', cursor=1",
     "SPEECH OUTPUT: 'Use tab key to reach the tab. Once a tab has focus use:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow", 
    ["BRAILLE LINE:  '• left and right arrows to move from tab to tab. Panel is made visible when tab gets focus. Arrow keys do not'",
     "     VISIBLE:  '• left and right arrows to move ', cursor=1",
     "SPEECH OUTPUT: '• left and right arrows to move from tab to tab. Panel is made visible when tab gets focus. Arrow keys do not'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down Arrow", 
    ["BRAILLE LINE:  'cycle around the tabs'",
     "     VISIBLE:  'cycle around the tabs', cursor=1",
     "SPEECH OUTPUT: 'cycle around the tabs'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down Arrow", 
    ["BRAILLE LINE:  '• ctrl-left and ctrl-right arrows behave the same as left and right arrows'",
     "     VISIBLE:  '• ctrl-left and ctrl-right arrow', cursor=1",
     "SPEECH OUTPUT: '• ctrl-left and ctrl-right arrows behave the same as left and right arrows'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down Arrow", 
    ["BRAILLE LINE:  '• ctrl-shift-pageup / ctrl-shift-pagedown is the same as left and right arrows but WILL cycle around the tab'",
     "     VISIBLE:  '• ctrl-shift-pageup / ctrl-shift', cursor=1",
     "SPEECH OUTPUT: '• ctrl-shift-pageup / ctrl-shift-pagedown is the same as left and right arrows but WILL cycle around the tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow", 
    ["BRAILLE LINE:  'order \(shift was added as a modifier so as not to conflict with the Firefox tabbing keys\)'",
     "     VISIBLE:  'order \(shift was added as a modi', cursor=1",
     "SPEECH OUTPUT: 'order \(shift was added as a modifier so as not to conflict with the Firefox tabbing keys\)'"]))

########################################################################
# Up Arrow through the panel text back to the page tab.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BRAILLE LINE:  '• ctrl-shift-pageup / ctrl-shift-pagedown is the same as left and right arrows but WILL cycle around the tab'",
     "     VISIBLE:  '• ctrl-shift-pageup / ctrl-shift', cursor=1",
     "SPEECH OUTPUT: '• ctrl-shift-pageup / ctrl-shift-pagedown is the same as left and right arrows but WILL cycle around the tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BRAILLE LINE:  '• ctrl-left and ctrl-right arrows behave the same as left and right arrows'",
     "     VISIBLE:  '• ctrl-left and ctrl-right arrow', cursor=1",
     "SPEECH OUTPUT: '• ctrl-left and ctrl-right arrows behave the same as left and right arrows'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    ["BRAILLE LINE:  'cycle around the tabs'",
     "     VISIBLE:  'cycle around the tabs', cursor=1",
     "SPEECH OUTPUT: 'cycle around the tabs'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow", 
    ["BRAILLE LINE:  '• left and right arrows to move from tab to tab. Panel is made visible when tab gets focus. Arrow keys do not'",
     "     VISIBLE:  '• left and right arrows to move ', cursor=1",
     "SPEECH OUTPUT: '• left and right arrows to move from tab to tab. Panel is made visible when tab gets focus. Arrow keys do not'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow", 
    ["BRAILLE LINE:  'Use tab key to reach the tab. Once a tab has focus use:'",
     "     VISIBLE:  'Use tab key to reach the tab. On', cursor=1",
     "SPEECH OUTPUT: 'Use tab key to reach the tab. Once a tab has focus use:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up Arrow", 
    ["BRAILLE LINE:  'namespaces, which is now the correct markup.'",
     "     VISIBLE:  'namespaces, which is now the cor', cursor=1",
     "SPEECH OUTPUT: 'namespaces, which is now the correct markup.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Up Arrow", 
    ["BRAILLE LINE:  'This example requires Firefox 3 or later to work with screen readers -- it uses ARIA properties without'",
     "     VISIBLE:  'This example requires Firefox 3 ', cursor=1",
     "SPEECH OUTPUT: 'This example requires Firefox 3 or later to work with screen readers -- it uses ARIA properties without'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Up Arrow", 
    ["BRAILLE LINE:  'Tab Zero Page'",
     "     VISIBLE:  'Tab Zero Page', cursor=1",
     "SPEECH OUTPUT: 'Tab Zero scroll pane'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Up Arrow", 
    ["BUG? - Not presenting anything for the final arrow"]))

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
