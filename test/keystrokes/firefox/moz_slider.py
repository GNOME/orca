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
# Tab to the slider.  The following will be presented.
# [[[Bug?: is Braille output correct?]]]
#
#  BRAILLE LINE:  '0 Move slider left Button 10 Slider Move slider right Button 100'
#       VISIBLE:  '10 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'slider 10'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("My slider", acc_role=pyatspi.ROLE_SLIDER))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  '0 Move slider left Button Move slider right Button 100'
#      VISIBLE:  '0 Move slider left Button Move s', cursor=0
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'slider'
# SPEECH OUTPUT: '10.0'
# SPEECH OUTPUT: '10 percent'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Move the slider.  The following will be presented for each.
#
#  BRAILLE LINE:  '0 Move slider left Button 15 Slider Move slider right Button 100'
#       VISIBLE:  '15 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '15'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '0 Move slider left Button 20 Slider Move slider right Button 100'
#       VISIBLE:  '20 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '20'                           
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '0 Move slider left Button 25 Slider Move slider right Button 100'
#       VISIBLE:  '25 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '25'                           
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '0 Move slider left Button 30 Slider Move slider right Button 100'
#       VISIBLE:  '30 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '30'                  
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '0 Move slider left Button 25 Slider Move slider right Button 100'
#       VISIBLE:  '25 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '25'                           
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '0 Move slider left Button 20 Slider Move slider right Button 100'
#       VISIBLE:  '20 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '20'                           
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '0 Move slider left Button 15 Slider Move slider right Button 100'
#       VISIBLE:  '15 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '15'                           
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  BRAILLE LINE:  '0 Move slider left Button 10 Slider Move slider right Button 100'
#       VISIBLE:  '10 Slider Move slider right Butt', cursor=1
# SPEECH OUTPUT: '10'                           
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  Move the slider with the 'end' key.
#
#  BRAILLE LINE:  '0 Move slider left Button 100 Slider Move slider right Button 100'
#       VISIBLE:  '100 Slider Move slider right But', cursor=1
# SPEECH OUTPUT: '100'                           
sequence.append(KeyComboAction("End"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
                           
#  Move the slider with the 'home' key.
#
#  BRAILLE LINE:  '0 Move slider left Button 0 Slider Move slider right Button 100'
#       VISIBLE:  '0 Slider Move slider right But', cursor=1
# SPEECH OUTPUT: '0'                               
sequence.append(KeyComboAction("Home"))
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
