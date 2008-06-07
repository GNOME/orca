#!/usr/bin/python

"""Test of UIUC slider presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Slider Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/slider/view_inline.php?title=Slider%20Example%201&ginc=includes/slider1_inline.inc&gcss=css/slider1.css&gjs=../js/globals.js,../js/widgets_inline.js,js/slider1_inline.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())


########################################################################
# Tab to slider 1
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to slider 1", 
    ["BRAILLE LINE:  'Slider Control 1 50 Slider'",
     "     VISIBLE:  'Slider Control 1 50 Slider', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Slider Control 1 slider 50'"]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Slider Control 1 50 Slider'",
     "     VISIBLE:  'Slider Control 1 50 Slider', cursor=1",
     "SPEECH OUTPUT: 'Slider Control 1'",
     "SPEECH OUTPUT: 'slider'",
     "SPEECH OUTPUT: '50.0'",
     "SPEECH OUTPUT: '50 percent'",
     "SPEECH OUTPUT: ''"]))
    
########################################################################
# Increment slider several times
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1 Increment slider 1", 
    ["BRAILLE LINE:  'Slider Control 1 51 Slider'",
     "     VISIBLE:  'Slider Control 1 51 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 1 51 Slider'",
     "     VISIBLE:  'Slider Control 1 51 Slider', cursor=1",
     "SPEECH OUTPUT: '51'",
     "SPEECH OUTPUT: '51'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2 Increment slider 1", 
    ["BRAILLE LINE:  'Slider Control 1 52 Slider'",
     "     VISIBLE:  'Slider Control 1 52 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 1 52 Slider'",
     "     VISIBLE:  'Slider Control 1 52 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 1 52 Slider'",
     "     VISIBLE:  'Slider Control 1 52 Slider', cursor=1",
     "SPEECH OUTPUT: '52'",
     "SPEECH OUTPUT: '52'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3 Increment slider 1", 
    ["BRAILLE LINE:  'Slider Control 1 53 Slider'",
     "     VISIBLE:  'Slider Control 1 53 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 1 53 Slider'",
     "     VISIBLE:  'Slider Control 1 53 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 1 53 Slider'",
     "     VISIBLE:  'Slider Control 1 53 Slider', cursor=1",
     "SPEECH OUTPUT: '53'",
     "SPEECH OUTPUT: '53'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4 Increment slider 1", 
    ["BRAILLE LINE:  'Slider Control 1 54 Slider'",
     "     VISIBLE:  'Slider Control 1 54 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 1 54 Slider'",
     "     VISIBLE:  'Slider Control 1 54 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 1 54 Slider'",
     "     VISIBLE:  'Slider Control 1 54 Slider', cursor=1",
     "SPEECH OUTPUT: '54'",
     "SPEECH OUTPUT: '54'"]))
    
########################################################################
# Tab to slider 2
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to slider 2", 
    ["BRAILLE LINE:  'Slider Control 2 100 Slider'",
     "     VISIBLE:  'Slider Control 2 100 Slider', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Slider Control 2 slider 100'"]))
    
########################################################################
# Decrement slider 2 several times
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1 Decrement slider 2", 
    ["BRAILLE LINE:  'Slider Control 2 101 Slider'",
     "     VISIBLE:  'Slider Control 2 101 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 2 101 Slider'",
     "     VISIBLE:  'Slider Control 2 101 Slider', cursor=1",
     "SPEECH OUTPUT: '101'",
     "SPEECH OUTPUT: '101'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2 Decrement slider 2", 
    ["BRAILLE LINE:  'Slider Control 2 102 Slider'",
     "     VISIBLE:  'Slider Control 2 102 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 2 102 Slider'",
     "     VISIBLE:  'Slider Control 2 102 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 2 102 Slider'",
     "     VISIBLE:  'Slider Control 2 102 Slider', cursor=1",
     "SPEECH OUTPUT: '102'",
     "SPEECH OUTPUT: '102'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3 Decrement slider 2", 
    ["BRAILLE LINE:  'Slider Control 2 103 Slider'",
     "     VISIBLE:  'Slider Control 2 103 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 2 103 Slider'",
     "     VISIBLE:  'Slider Control 2 103 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 2 103 Slider'",
     "     VISIBLE:  'Slider Control 2 103 Slider', cursor=1",
     "SPEECH OUTPUT: '103'",
     "SPEECH OUTPUT: '103'"]))
    
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4 Decrement slider 2", 
    ["BRAILLE LINE:  'Slider Control 2 104 Slider'",
     "     VISIBLE:  'Slider Control 2 104 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 2 104 Slider'",
     "     VISIBLE:  'Slider Control 2 104 Slider', cursor=1",
     "BRAILLE LINE:  'Slider Control 2 104 Slider'",
     "     VISIBLE:  'Slider Control 2 104 Slider', cursor=1",
     "SPEECH OUTPUT: '104'",
     "SPEECH OUTPUT: '104'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
