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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/pretty-slider.htm"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Graphical ARIA Slider", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first slider.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 10 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '10 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'slider 10'"]))
     

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 10 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '10 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'slider'",
     "SPEECH OUTPUT: '10.0'",
     "SPEECH OUTPUT: '10 percent'",
     "SPEECH OUTPUT: ''"]))

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
    ["BRAILLE LINE:  '0 Cell Move slider left Button 15 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '15 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '15'"]))
                               
sequence.append(utils.StartRecordingAction())                       
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "1 move slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 20 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '20 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '20'"]))
                              
sequence.append(utils.StartRecordingAction())                         
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "2 move slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 25 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '25 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '25'"]))
                                     
sequence.append(utils.StartRecordingAction())           
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "3 move slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 30 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '30 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '30'"]))
                               
sequence.append(utils.StartRecordingAction())                        
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "4 move slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 25 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '25 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '25'"]))
                                       
sequence.append(utils.StartRecordingAction())                  
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "5 move slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 20 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '20 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '20'"]))
                                     
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "6 move slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 15 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '15 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '15'"]))                           
  
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "7 move slider", 
    ["BRAILLE LINE:  '0 Cell Move slider left Button 10 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '10 Slider Move slider right Butt', cursor=1",
     "SPEECH OUTPUT: '10'"]))   
                            
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
    ["BRAILLE LINE:  '0 Cell Move slider left Button 100 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '100 Slider Move slider right But', cursor=1",
     "SPEECH OUTPUT: '100'"]))
                               
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
    ["BRAILLE LINE:  '0 Cell Move slider left Button 0 Slider Move slider right Button 100 Cell'",
     "     VISIBLE:  '0 Slider Move slider right Butto', cursor=1",
     "SPEECH OUTPUT: '0'"]))
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
