#!/usr/bin/python

"""Test of Dojo slider presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dojo Slider Widget Demo" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "form/test_Slider.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dojo Slider Widget Demo", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget plenty of time to construct itself. 
#
sequence.append(PauseAction(10000))

########################################################################
# Tab to the first slider.  The following will be presented.
#
#  BRAILLE LINE:  '10 Slider'
#       VISIBLE:  '10 Slider', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'slider 10'
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab", 1000))
sequence.append(utils.AssertPresentationAction(
    "tab to first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10 Sli', cursor=1",
     "SPEECH OUTPUT: 'Horizontal Slider Example table'",
     "SPEECH OUTPUT: 'Horizontal Slider Example slider 10'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE: 
#      VISIBLE:  
# SPEECH OUTPUT:
#
# sequence.append(KeyComboAction("KP_Enter"))
# sequence.append(PauseAction(3000))

########################################################################
# Move the first slider several times.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "1 move first slider", 
    ["KNOWN ISSUE - crazy valuetext http://bugs.dojotoolkit.org/ticket/8539",
     "BRAILLE LINE:  'Horizontal Slider Example 10.242130750605327 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.242', cursor=1",
     "SPEECH OUTPUT: '10.242130750605327'"]))
                            
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "2 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10.484261501210653 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.484', cursor=1",
     "SPEECH OUTPUT: '10.484261501210653'"]))
                               
sequence.append(utils.StartRecordingAction())                      
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "3 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10.72639225181598 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.726', cursor=1",
     "SPEECH OUTPUT: '10.72639225181598'"]))
                           
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "4 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10.968523002421307 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.968', cursor=1",
     "SPEECH OUTPUT: '10.968523002421307'"]))
                               
sequence.append(utils.StartRecordingAction())                  
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "5 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 11.210653753026634 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 11.210', cursor=1",
     "SPEECH OUTPUT: '11.210653753026634'"]))
                                  
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "6 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10.968523002421307 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.968', cursor=1",
     "SPEECH OUTPUT: '10.968523002421307'"]))
                                 
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "7 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10.72639225181598 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.726', cursor=1",
     "SPEECH OUTPUT: '10.72639225181598'"]))
                                  
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "8 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10.484261501210653 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.484', cursor=1",
     "SPEECH OUTPUT: '10.484261501210653'"]))
                             
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "9 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10.242130750605327 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10.242', cursor=1",
     "SPEECH OUTPUT: '10.242130750605327'"]))
                            
sequence.append(utils.StartRecordingAction())                       
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "10 move first slider", 
    ["BRAILLE LINE:  'Horizontal Slider Example 10 Slider'",
     "     VISIBLE:  'Horizontal Slider Example 10 Sli', cursor=1",
     "SPEECH OUTPUT: '10'"]))

########################################################################
# Tab to the next entry between the sliders. 
# [[[Bug?: not labeling properly.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "move to entry", 
    ["BRAILLE LINE:  '10.0% $l rdonly'",
     "     VISIBLE:  '10.0% $l rdonly', cursor=0",
     "BRAILLE LINE:  '10.0% $l rdonly'",
     "     VISIBLE:  '10.0% $l rdonly', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Slider1 Value: read only text 10.0%'"]))

########################################################################
# Tab to the button between the sliders.  
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "move to button", 
    ["BRAILLE LINE:  'Disable previous slider Button Enable previous slider Button'",
     "     VISIBLE:  'Disable previous slider Button E', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Disable previous slider button'"]))
     
########################################################################
# Tab to the next slider.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 10 Slider'",
     "     VISIBLE:  'Vertical Slider Example 10 Slide', cursor=1",
     "SPEECH OUTPUT: 'Vertical Slider Example table'",
     "SPEECH OUTPUT: 'Vertical Slider Example slider 10'"]))

########################################################################
# Move the slider several times
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "1 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 20 Slider'",
     "     VISIBLE:  'Vertical Slider Example 20 Slide', cursor=1",
     "SPEECH OUTPUT: '20'"]))

sequence.append(utils.StartRecordingAction())                       
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "2 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 30 Slider'",
     "     VISIBLE:  'Vertical Slider Example 30 Slide', cursor=1",
     "SPEECH OUTPUT: '30'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "3 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 40 Slider'",
     "     VISIBLE:  'Vertical Slider Example 40 Slide', cursor=1",
     "SPEECH OUTPUT: '40'"]))

sequence.append(utils.StartRecordingAction())                        
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "4 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 50 Slider'",
     "     VISIBLE:  'Vertical Slider Example 50 Slide', cursor=1",
     "SPEECH OUTPUT: '50'"]))
  
sequence.append(utils.StartRecordingAction())                        
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "5 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 60 Slider'",
     "     VISIBLE:  'Vertical Slider Example 60 Slide', cursor=1",
     "SPEECH OUTPUT: '60'"]))
                               
sequence.append(utils.StartRecordingAction())                       
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "6 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 50 Slider'",
     "     VISIBLE:  'Vertical Slider Example 50 Slide', cursor=1",
     "SPEECH OUTPUT: '50'"]))
 
sequence.append(utils.StartRecordingAction())                        
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "7 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 40 Slider'",
     "     VISIBLE:  'Vertical Slider Example 40 Slide', cursor=1",
     "SPEECH OUTPUT: '40'"]))
                               
sequence.append(utils.StartRecordingAction())                        
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "8 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 30 Slider'",
     "     VISIBLE:  'Vertical Slider Example 30 Slide', cursor=1",
     "SPEECH OUTPUT: '30'"]))
                                 
sequence.append(utils.StartRecordingAction())                         
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "9 move second slider", 
    ["BRAILLE LINE:  'Vertical Slider Example 20 Slider'",
     "     VISIBLE:  'Vertical Slider Example 20 Slide', cursor=1",
     "SPEECH OUTPUT: '20'"]))
    
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
