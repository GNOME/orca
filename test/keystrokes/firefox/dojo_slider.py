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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the dojo slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "form/test_Slider.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dojo Slider Widget Demo", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

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
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'slider 10'"]))

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
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
     "SPEECH OUTPUT: '10'"]))
                            
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "2 move first slider", 
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
     "SPEECH OUTPUT: '10'"]))
                               
sequence.append(utils.StartRecordingAction())                      
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "3 move first slider", 
    ["BRAILLE LINE:  '11 Slider'",
     "     VISIBLE:  '11 Slider', cursor=1",
     "SPEECH OUTPUT: '11'"]))
                           
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "4 move first slider", 
    ["BRAILLE LINE:  '11 Slider'",
     "     VISIBLE:  '11 Slider', cursor=1",
     "SPEECH OUTPUT: '11'"]))
                               
sequence.append(utils.StartRecordingAction())                  
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "5 move first slider", 
    ["BRAILLE LINE:  '11 Slider'",
     "     VISIBLE:  '11 Slider', cursor=1",
     "SPEECH OUTPUT: '11'"]))
                                  
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "6 move first slider", 
    ["BRAILLE LINE:  '11 Slider'",
     "     VISIBLE:  '11 Slider', cursor=1",
     "SPEECH OUTPUT: '11'"]))
                                 
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "7 move first slider", 
    ["BRAILLE LINE:  '11 Slider'",
     "     VISIBLE:  '11 Slider', cursor=1",
     "SPEECH OUTPUT: '11'"]))
                                  
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "8 move first slider", 
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
     "SPEECH OUTPUT: '10'"]))
                             
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "9 move first slider", 
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
     "SPEECH OUTPUT: '10'"]))
                            
sequence.append(utils.StartRecordingAction())                       
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "10 move first slider", 
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
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
    ["BUG? - We're guessing other text in addition to the label",
     "BRAILLE LINE:  'Slider1 Value: 10.0% $l'",
     "     VISIBLE:  'Slider1 Value: 10.0% $l', cursor=21",
     "BRAILLE LINE:  'Slider1 Value: 10.0% $l'",
     "     VISIBLE:  'Slider1 Value: 10.0% $l', cursor=21",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'initial value=10, min=0, max=100, pageIncrement=100, onChange event triggers input box value change immediately",
     "Slider1 Value: text 10.0%'"]))
     
########################################################################
# Tab to the button between the sliders.  
# [[[Bug?: whitespace.  below are expected results]]]
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "move to button", 
    ["BRAILLE LINE:  'Disable previous slider Button'",
     "     VISIBLE:  'Disable previous slider Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Disable previous slider button'"]))
     
########################################################################
# Tab to the next slider.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to second slider", 
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'slider 10'"]))

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
    ["BRAILLE LINE:  '20 Slider'",
     "     VISIBLE:  '20 Slider', cursor=1",
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
    ["BRAILLE LINE:  '30 Slider'",
     "     VISIBLE:  '30 Slider', cursor=1",
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
    ["BRAILLE LINE:  '40 Slider'",
     "     VISIBLE:  '40 Slider', cursor=1",
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
    ["BRAILLE LINE:  '50 Slider'",
     "     VISIBLE:  '50 Slider', cursor=1",
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
    ["BRAILLE LINE:  '60 Slider'",
     "     VISIBLE:  '60 Slider', cursor=1",
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
    ["BRAILLE LINE:  '50 Slider'",
     "     VISIBLE:  '50 Slider', cursor=1",
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
    ["BRAILLE LINE:  '40 Slider'",
     "     VISIBLE:  '40 Slider', cursor=1",
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
    ["BRAILLE LINE:  '30 Slider'",
     "     VISIBLE:  '30 Slider', cursor=1",
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
    ["BRAILLE LINE:  '20 Slider'",
     "     VISIBLE:  '20 Slider', cursor=1",
     "SPEECH OUTPUT: '20'"]))
    
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
