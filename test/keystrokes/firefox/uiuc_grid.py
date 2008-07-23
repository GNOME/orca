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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/grid/view_inline.php?title=Grid%20Example%201:%20E-mail%20List%20with%20Row%20and%20Column%20Navigation&ginc=includes/grid1_inline.inc&gcss=css/grid1.css&gjs=../js/globals.js,../js/widgets_inline.js,js/grid1.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(3000))

########################################################################
# Tab to grid
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to grid", 
    ["BRAILLE LINE:  'E-mail List Sorted by Date Caption Sel $l'",
     "     VISIBLE:  'E-mail List Sorted by Date Capti', cursor=0",
     "BRAILLE LINE:  '< > Email 0 Selected CheckBox 1 Cell Read message Image Attachment Image Lowest priority Image John Smith Cell Trip to Florida Cell 2007-10-03 Cell 2K Cell'",
     "     VISIBLE:  '< > Email 0 Selected CheckBox 1 ', cursor=1",
     "BRAILLE LINE:  '< > Email 0 Selected CheckBox 1 Cell Read message Image Attachment Image Lowest priority Image John Smith Cell Trip to Florida Cell 2007-10-03 Cell 2K Cell'",
     "     VISIBLE:  '< > Email 0 Selected CheckBox 1 ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'E-mail List Sorted by Date table'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Status column header'",
     "SPEECH OUTPUT: '1 Read message Attachment Lowest priority From John Smith Subject Trip to Florida panel'"]))
    
########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  '< > Email 0 Selected CheckBox 1 Cell Read message Image Attachment Image Lowest priority Image John Smith Cell Trip to Florida Cell 2007-10-03 Cell 2K Cell'",
     "     VISIBLE:  '< > Email 0 Selected CheckBox 1 ', cursor=1",
     "SPEECH OUTPUT: '1 Read message Attachment Lowest priority From John Smith Subject Trip to Florida'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: '1 Read message Attachment Lowest priority John Smith Trip to Florida'"]))
    
########################################################################
# Move down grid
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Move down grid", 
    ["BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '< > Email 1 Selected CheckBox 2 ', cursor=1",
     "BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '< > Email 1 Selected CheckBox 2 ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Att column header'",
     "SPEECH OUTPUT: '2 New message Attachment Low priority From Fred Jones Subject Lunch on Friday panel'",
     "SPEECH OUTPUT: 'check box not checked 2 New message image Attachment image Low priority image Fred Jones Lunch on Friday 2007-12-03 1K'"]))
    
########################################################################
# Move right on second row 1
#   
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move right on second row 1", 
    ["BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '< > Email 1 Selected CheckBox 2 ', cursor=1",
     "BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '< > Email 1 Selected CheckBox 2 ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Email 1 Selected'"]))
     
########################################################################
# Move right on second row 2
#   
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move right on second row 2", 
    ["BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '2 Cell New message Image Attachm', cursor=1",
     "BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  '2 Cell New message Image Attachm', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '2'",
     "SPEECH OUTPUT: '2'"]))
     
########################################################################
# Move right on second row 3
#   
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Move right on second row 3", 
    ["BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
     "     VISIBLE:  'New message Image Attachment Ima', cursor=1",
     "BRAILLE LINE:  '< > Email 1 Selected CheckBox 2 Cell New message Image Attachment Image Low priority Image Fred Jones Cell Lunch on Friday Cell 2007-12-03 Cell 1K Cell'",
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
    ["BRAILLE LINE:  '< > Email 2 Selected CheckBox 3 Cell New message Image None Image Jane Johnson Cell Proposal for you to review Cell 2007-16-03 Cell 12K Cell'",
     "     VISIBLE:  'New message Image None Image Jan', cursor=1",
     "BRAILLE LINE:  '< > Email 2 Selected CheckBox 3 Cell New message Image None Image Jane Johnson Cell Proposal for you to review Cell 2007-16-03 Cell 12K Cell'",
     "     VISIBLE:  'New message Image None Image Jan', cursor=1",
     "SPEECH OUTPUT: '3 New message None From Jane Johnson Subject Proposal for you to review panel'",
     "SPEECH OUTPUT: 'New message'",
     "SPEECH OUTPUT: 'check box not checked 3 New message image None image Jane Johnson Proposal for you to review 2007-16-03 12K'"]))

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
