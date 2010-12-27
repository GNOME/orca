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
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "form/test_Slider.html"))
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
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab", 1000))
sequence.append(utils.AssertPresentationAction(
    "tab to first slider", 
    ["BRAILLE LINE:  '10 Slider'",
     "     VISIBLE:  '10 Slider', cursor=1",
     "SPEECH OUTPUT: 'slider 10'"]))

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
     "BRAILLE LINE:  '10.22271714922049 Slider'",
     "     VISIBLE:  '10.22271714922049 Slider', cursor=1",
     "SPEECH OUTPUT: '10.22271714922049'"]))
                            
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "2 move first slider", 
    ["BRAILLE LINE:  '10.44543429844098 Slider'",
     "     VISIBLE:  '10.44543429844098 Slider', cursor=1",
     "SPEECH OUTPUT: '10.44543429844098'"]))
                               
sequence.append(utils.StartRecordingAction())                      
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "3 move first slider", 
    ["BRAILLE LINE:  '10.66815144766147 Slider'",
     "     VISIBLE:  '10.66815144766147 Slider', cursor=1",
     "SPEECH OUTPUT: '10.66815144766147'"]))
                           
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "4 move first slider", 
    ["BRAILLE LINE:  '10.89086859688196 Slider'",
     "     VISIBLE:  '10.89086859688196 Slider', cursor=1",
     "SPEECH OUTPUT: '10.89086859688196'"]))
                               
sequence.append(utils.StartRecordingAction())                  
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "5 move first slider", 
    ["BRAILLE LINE:  '11.11358574610245 Slider'",
     "     VISIBLE:  '11.11358574610245 Slider', cursor=1",
     "SPEECH OUTPUT: '11.11358574610245'"]))
                                  
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "6 move first slider", 
    ["BRAILLE LINE:  '10.89086859688196 Slider'",
     "     VISIBLE:  '10.89086859688196 Slider', cursor=1",
     "SPEECH OUTPUT: '10.89086859688196'"]))
                                 
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "7 move first slider", 
    ["BRAILLE LINE:  '10.66815144766147 Slider'",
     "     VISIBLE:  '10.66815144766147 Slider', cursor=1",
     "SPEECH OUTPUT: '10.66815144766147'"]))
                                  
sequence.append(utils.StartRecordingAction())                    
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "8 move first slider", 
    ["BRAILLE LINE:  '10.44543429844098 Slider'",
     "     VISIBLE:  '10.44543429844098 Slider', cursor=1",
     "SPEECH OUTPUT: '10.44543429844098'"]))
                             
sequence.append(utils.StartRecordingAction())                     
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "9 move first slider", 
    ["BRAILLE LINE:  '10.22271714922049 Slider'",
     "     VISIBLE:  '10.22271714922049 Slider', cursor=1",
     "SPEECH OUTPUT: '10.22271714922049'"]))
                            
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
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "move to entry", 
    ["BRAILLE LINE:  'Slider1 Value: 10.0% $l rdonly'",
     "     VISIBLE:  'Slider1 Value: 10.0% $l rdonly', cursor=0",
     "BRAILLE LINE:  'Slider1 Value: 10.0% $l rdonly'",
     "     VISIBLE:  'Slider1 Value: 10.0% $l rdonly', cursor=0",
     "SPEECH OUTPUT: 'Slider1 Value: read only text 10.0% selected'"]))

########################################################################
# Tab to the button between the sliders.  
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "move to button", 
    ["BUG? - Why no braille?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
