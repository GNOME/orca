#!/usr/bin/python

"""Test of Mozilla ARIA slider presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Graphical ARIA Slider" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the Mozilla ARIA slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/pretty-slider.htm"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Graphical ARIA Slider", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))
sequence.append(PauseAction(3000))

########################################################################
# Tab to the first slider.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to slider", 
    ["BRAILLE LINE:  '10% Slider'",
     "     VISIBLE:  '10% Slider', cursor=1",
     "SPEECH OUTPUT: 'My slider slider 10%'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  '10% Slider'",
     "     VISIBLE:  '10% Slider', cursor=1",
     "SPEECH OUTPUT: 'slider 10.0 10 percent '"]))

########################################################################
# Move the slider several times.  The following will be presented for each.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "0 move slider", 
    ["BRAILLE LINE:  '$15.00 Slider'",
     "     VISIBLE:  '$15.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$15.00'"]))
                               
sequence.append(utils.StartRecordingAction())                       
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "1 move slider", 
    ["BRAILLE LINE:  '$20.00 Slider'",
     "     VISIBLE:  '$20.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$20.00'"]))
                              
sequence.append(utils.StartRecordingAction())                         
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "2 move slider", 
    ["BRAILLE LINE:  '$25.00 Slider'",
     "     VISIBLE:  '$25.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$25.00'"]))
                                     
sequence.append(utils.StartRecordingAction())           
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "3 move slider", 
    ["BRAILLE LINE:  '$30.00 Slider'",
     "     VISIBLE:  '$30.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$30.00'"]))
                               
sequence.append(utils.StartRecordingAction())                        
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "4 move slider", 
    ["BRAILLE LINE:  '$25.00 Slider'",
     "     VISIBLE:  '$25.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$25.00'"]))
                                       
sequence.append(utils.StartRecordingAction())                  
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "5 move slider", 
    ["BRAILLE LINE:  '$20.00 Slider'",
     "     VISIBLE:  '$20.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$20.00'"]))
                                     
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "6 move slider", 
    ["BRAILLE LINE:  '$15.00 Slider'",
     "     VISIBLE:  '$15.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$15.00'"]))                           
  
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "7 move slider", 
    ["BRAILLE LINE:  '$10.00 Slider'",
     "     VISIBLE:  '$10.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$10.00'"]))   
                            
#  Move the slider with the 'end' key.
#         
sequence.append(utils.StartRecordingAction())                
sequence.append(KeyComboAction("End"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "move slider end", 
    ["BRAILLE LINE:  '$100.00 Slider'",
     "     VISIBLE:  '$100.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$100.00'"]))
                               
#  Move the slider with the 'home' key.
#                
sequence.append(utils.StartRecordingAction())              
sequence.append(KeyComboAction("Home"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "move slider home", 
    ["BRAILLE LINE:  '$0.00 Slider'",
     "     VISIBLE:  '$0.00 Slider', cursor=1",
     "SPEECH OUTPUT: '$0.00'"]))

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
