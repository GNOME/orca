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
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SLIDER))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE: 
#      VISIBLE:  
# SPEECH OUTPUT:
#
# [[[Bug?: dojo is not providing correct value information which throws an
# exception on our side]]]
# sequence.append(KeyComboAction("KP_Enter"))
# sequence.append(PauseAction(3000))

########################################################################
# Move the first slider.  The following will be presented for each.
#
#  BRAILLE LINE:  '10 Slider'
#       VISIBLE:  '10 Slider', cursor=1
# SPEECH OUTPUT: '10'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '10 Slider'
#       VISIBLE:  '10 Slider', cursor=1
# SPEECH OUTPUT: '10'                           
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
# BRAILLE LINE:  '11 Slider'
#      VISIBLE:  '11 Slider', cursor=1
# SPEECH OUTPUT: '11'                           
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
# BRAILLE LINE:  '11 Slider'
#      VISIBLE:  '11 Slider', cursor=1
# SPEECH OUTPUT: '11' 
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
# BRAILLE LINE:  '11 Slider'
#      VISIBLE:  '11 Slider', cursor=1
# SPEECH OUTPUT: '11'                           
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
# BRAILLE LINE:  '11 Slider'
#      VISIBLE:  '11 Slider', cursor=1
# SPEECH OUTPUT: '11'                             
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
# BRAILLE LINE:  '11 Slider'
#      VISIBLE:  '11 Slider', cursor=1
# SPEECH OUTPUT: '11'                             
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '10 Slider'
#       VISIBLE:  '10 Slider', cursor=1
# SPEECH OUTPUT: '10'                            
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '10 Slider'
#       VISIBLE:  '10 Slider', cursor=1
# SPEECH OUTPUT: '10'                            
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '10 Slider'
#       VISIBLE:  '10 Slider', cursor=1
# SPEECH OUTPUT: '10'                           
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))

########################################################################
# Tab to the next entry between the sliders.  The following will be presented.
# [[[Bug?: entry should be labelled for speech]]]
#
#  BRAILLE LINE:  'Slider1 Value: 10 $l '
#       VISIBLE:  'Slider1 Value: 10 $l ', cursor=18
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'text 10'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

########################################################################
# Tab to the next slider.  The following will be presented.
#
#  BRAILLE LINE:  '10 Slider'
#       VISIBLE:  '10 Slider', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'slider 10'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SLIDER))

########################################################################
# Move the slider.  The following will be presented for each.
#
#  BRAILLE LINE:  '20 Slider 20 '
#       VISIBLE:  '20 Slider 20 ', cursor=1
# SPEECH OUTPUT: '20'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '30 Slider'
#       VISIBLE:  '30 Slider', cursor=1
# SPEECH OUTPUT: '30'                          
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                       
#  BRAILLE LINE:  '40 Slider'
#       VISIBLE:  '40 Slider', cursor=1
# SPEECH OUTPUT: '40' 
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '50 Slider'
#       VISIBLE:  '50 Slider', cursor=1
# SPEECH OUTPUT: '50'                            
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '60 Slider'
#       VISIBLE:  '60 Slider', cursor=1
# SPEECH OUTPUT: '60'                            
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '50 Slider'
#       VISIBLE:  '50 Slider', cursor=1
# SPEECH OUTPUT: '50'                            
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '40 Slider'
#       VISIBLE:  '40 Slider', cursor=1
# SPEECH OUTPUT: '40'                            
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '30 Slider'
#       VISIBLE:  '30 Slider', cursor=1
# SPEECH OUTPUT: '30'                            
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '20 Slider'
#       VISIBLE:  '20 Slider', cursor=1
# SPEECH OUTPUT: '20'                            
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))

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

sequence.start()
