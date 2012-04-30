#!/usr/bin/python
'''TEST	the Ability to find out the square root of a selected number'''

from macaroon.playback import *
import utils
sequence = MacroSequence()

###############################################################################
# Use the 'Advanced' mode...
#
sequence.append(WaitForWindowActivate("Calculator", None))
sequence.append(KeyComboAction("<Control>a"))
sequence.append(WaitForFocus("Change Mode", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

###############################################################################
# Input the number 144 and find its square root.
#
sequence.append(WaitForWindowActivate("Calculator - Advanced", None))
sequence.append(TypeAction("s144)"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
"Get the answer '12'",
["BRAILLE LINE:  '12'",
"     VISIBLE:  '12', cursor=0",
"SPEECH OUTPUT: '12'"]))

###############################################################################
##Set Calculator to basic modul.
##Select 'Calculator'->'Quit' to exit.
##
sequence.append(KeyComboAction("<Control>b"))
	
# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()

