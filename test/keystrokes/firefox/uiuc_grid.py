#!/usr/bin/python

"""Test of UIUC grid presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Grid Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/grid/view_inline.php?title=Grid%20Example%201:%20E-mail%20List%20with%20Row%20and%20Column%20Navigation&ginc=includes/grid1_inline.inc&gcss=css/grid1.css&gjs=../js/globals.js,../js/widgets_inline.js,js/grid1.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Tab to grid
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to grid", 
    ["BRAILLE LINE:  'E-mail List Sorted by Date Caption'",
     "     VISIBLE:  'E-mail List Sorted by Date Capti', cursor=1",
     "BRAILLE LINE:  '< > Email 0 Selected CheckBox 1 Read message Image Attachment Image Lowest priority Image John Smith Trip to Florida 2007-10-03 2K'",
     "     VISIBLE:  '< > Email 0 Selected CheckBox 1 ', cursor=1",
     "BRAILLE LINE:  'Email 0 Selected CheckBox'",
     "     VISIBLE:  'Email 0 Selected CheckBox', cursor=0",
     "SPEECH OUTPUT: 'E-mail List Sorted by Date caption'",
     "SPEECH OUTPUT: 'check box not checked 1 Read message image Attachment image Lowest priority image John Smith Trip to Florida 2007-10-03 2K'"]))
  
########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BUG? - speech info is useless",
     "BRAILLE LINE:  'Email 0 Selected CheckBox'",
     "     VISIBLE:  'Email 0 Selected CheckBox', cursor=0",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: 'cell'"]))

########################################################################
# Move down grid
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move down grid", 
    ["BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '< > Email 1 Selected CheckBox 2 ', cursor=1",
     "BRAILLE LINE:  'Email 1 Selected CheckBox'",
     "     VISIBLE:  'Email 1 Selected CheckBox', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Att column header'",
     "SPEECH OUTPUT: '2 New message Attachment Low priority From Fred Jones Subject Lunch on Friday panel'",
     "SPEECH OUTPUT: 'Email 1 Selected'"]))
    
########################################################################
# Move right on second row 1
#   
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move right on second row 1", 
    ["BUG? - We're saying nothing here"]))
     
########################################################################
# Move right on second row 2
#   
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move right on second row 2", 
    ["BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '2 Cell New message Image Attachm', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '2'"]))
     
########################################################################
# Move right on second row 3
#   
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move right on second row 3", 
    ["BRAILLE LINE:  'New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  'New message Image Attachment Ima', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'New message'"]))
    
########################################################################
# Move down to third row 
#   
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move down to third row", 
    ["BRAILLE LINE:  'New message Image None Image Image Jane Johnson Cell Proposal for you to review Cell 2007-16-03 Cell 12K Cell'",
     "     VISIBLE:  'New message Image None Image Ima', cursor=1",
     "SPEECH OUTPUT: '3 New message None From Jane Johnson Subject Proposal for you to review panel'",
     "SPEECH OUTPUT: 'New message'"]))

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
