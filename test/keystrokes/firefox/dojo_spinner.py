#!/usr/bin/python

"""Test of Dojo spinner presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dojo Spinner Widget Test" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo spinner demo.
#
# NOTE: After 5 Aug 2009, the test sets the required state to False by
# Default. The state can be toggled by pressing a button, which is NOT
# in the Tab order. :-( Therefore, for now, use the most recent archive
# which has required set to True.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "form/test_Spinner.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dojo Spinner Widget Test", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself.  Move to the top of
# the file because that seems to give us more consistent results for
# the first test.
#
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

########################################################################
# Tab to the first spinner.  
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the first spinner",
    ["BRAILLE LINE:  'Spinbox #1: 900 $l required'",
     "     VISIBLE:  'Spinbox #1: 900 $l required', cursor=16",
     "SPEECH OUTPUT: 'Spinbox #1: 900 selected spin button required'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 1", 
    ["BRAILLE LINE:  'Spinbox #1: 900 $l required'",
     "     VISIBLE:  'Spinbox #1: 900 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 899 $l required'",
     "     VISIBLE:  'Spinbox #1: 899 $l required', cursor=16",
     "SPEECH OUTPUT: '899'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 2", 
    ["BRAILLE LINE:  'Spinbox #1: 899 $l required'",
     "     VISIBLE:  'Spinbox #1: 899 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 898 $l required'",
     "     VISIBLE:  'Spinbox #1: 898 $l required', cursor=16",
     "SPEECH OUTPUT: '898'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 3", 
    ["BRAILLE LINE:  'Spinbox #1: 898 $l required'",
     "     VISIBLE:  'Spinbox #1: 898 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 897 $l required'",
     "     VISIBLE:  'Spinbox #1: 897 $l required', cursor=16",
     "SPEECH OUTPUT: '897'"]))

########################################################################
# Use down arrow to decrement spinner value. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 4", 
    ["BRAILLE LINE:  'Spinbox #1: 897 $l required'",
     "     VISIBLE:  'Spinbox #1: 897 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 896 $l required'",
     "     VISIBLE:  'Spinbox #1: 896 $l required', cursor=16",
     "SPEECH OUTPUT: '896'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 5", 
    ["BRAILLE LINE:  'Spinbox #1: 896 $l required'",
     "     VISIBLE:  'Spinbox #1: 896 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 895 $l required'",
     "     VISIBLE:  'Spinbox #1: 895 $l required', cursor=16",
     "SPEECH OUTPUT: '895'"]))

########################################################################
# Use up arrow to increment spinner value. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 1", 
    ["BRAILLE LINE:  'Spinbox #1: 895 $l required'",
     "     VISIBLE:  'Spinbox #1: 895 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 896 $l required'",
     "     VISIBLE:  'Spinbox #1: 896 $l required', cursor=16",
     "SPEECH OUTPUT: '896'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 2", 
    ["BRAILLE LINE:  'Spinbox #1: 896 $l required'",
     "     VISIBLE:  'Spinbox #1: 896 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 897 $l required'",
     "     VISIBLE:  'Spinbox #1: 897 $l required', cursor=16",
     "SPEECH OUTPUT: '897'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 3", 
    ["BRAILLE LINE:  'Spinbox #1: 897 $l required'",
     "     VISIBLE:  'Spinbox #1: 897 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 898 $l required'",
     "     VISIBLE:  'Spinbox #1: 898 $l required', cursor=16",
     "SPEECH OUTPUT: '898'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 4", 
    ["BRAILLE LINE:  'Spinbox #1: 898 $l required'",
     "     VISIBLE:  'Spinbox #1: 898 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 899 $l required'",
     "     VISIBLE:  'Spinbox #1: 899 $l required', cursor=16",
     "SPEECH OUTPUT: '899'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 5", 
    ["BRAILLE LINE:  'Spinbox #1: 899 $l required'",
     "     VISIBLE:  'Spinbox #1: 899 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 900 $l required'",
     "     VISIBLE:  'Spinbox #1: 900 $l required', cursor=16",
     "SPEECH OUTPUT: '900'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 6", 
    ["BRAILLE LINE:  'Spinbox #1: 900 $l required'",
     "     VISIBLE:  'Spinbox #1: 900 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 901 $l required'",
     "     VISIBLE:  'Spinbox #1: 901 $l required', cursor=16",
     "SPEECH OUTPUT: '901'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 7", 
    ["BRAILLE LINE:  'Spinbox #1: 901 $l required'",
     "     VISIBLE:  'Spinbox #1: 901 $l required', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 902 $l required'",
     "     VISIBLE:  'Spinbox #1: 902 $l required', cursor=16",
     "SPEECH OUTPUT: '902'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Spinbox #1: 902 $l required'",
     "     VISIBLE:  'Spinbox #1: 902 $l required', cursor=16",
     "SPEECH OUTPUT: 'Spinbox #1: spin button 902 required'"]))

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
