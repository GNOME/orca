#!/usr/bin/python

"""Test of Yahoo's tab view presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Tab Panel Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://developer.yahoo.com/yui/examples/tabview/tabview-ariaplugin_clean.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Navigate to the tab view
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to the tab view",
    ["BUG? - Ultimately we get around to announcing the page tab, but should we be speaking all of that additional information?",
     "BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Opera Page Firefox Page Explorer', cursor=1",
     "SPEECH OUTPUT: 'Browser NewsPress the space bar or enter key to load the content of each tab. Browser News Press the space bar or enter key to load the content of each tab. tab list'",
     "SPEECH OUTPUT: 'Opera page'"]))
    
########################################################################
# Right Arrow to the second tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to the next tab", 
    ["BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Firefox Page Explorer Page Safar', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Firefox page'"]))

########################################################################
# Right Arrow to the third tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to the next tab", 
    ["BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Explorer Page Safari Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Explorer page'"]))

########################################################################
# Right Arrow to the fourth tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to the next tab", 
    ["BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Safari Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Safari page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Safari Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Safari page'",
     "SPEECH OUTPUT: 'item 4 of 4'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Left Arrow back to the third tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to the previous tab", 
    ["BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Explorer Page Safari Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Explorer page'"]))

########################################################################
# Left Arrow back to the second tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to the previous tab", 
    ["BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Firefox Page Explorer Page Safar', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Firefox page'"]))

########################################################################
# Left Arrow back to the first tab
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to the previous tab", 
    ["BRAILLE LINE:  'Opera Page Firefox Page Explorer Page Safari Page'",
     "     VISIBLE:  'Opera Page Firefox Page Explorer', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Opera page'"]))

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
