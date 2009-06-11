#!/usr/bin/python

"""Test of slider output using custom program.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and flat review to the progress bar
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SLIDER))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Slider Where Am I",
    ["BRAILLE LINE:  'slider Application Slider Frame Some slider: 0.0 Slider'",
     "     VISIBLE:  'Some slider: 0.0 Slider', cursor=1",
     "SPEECH OUTPUT: 'Some slider: slider 0.0 0 percent Alt s'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Increment value",
    ["BRAILLE LINE:  'slider Application Slider Frame Some slider: 1.0 Slider'",
     "     VISIBLE:  'Some slider: 1.0 Slider', cursor=1",
     "SPEECH OUTPUT: '1.0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Slider Where Am I",
    ["BRAILLE LINE:  'slider Application Slider Frame Some slider: 1.0 Slider'",
     "     VISIBLE:  'Some slider: 1.0 Slider', cursor=1",
     "SPEECH OUTPUT: 'Some slider: slider 1.0 10 percent Alt s'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Decrement value",
    ["BRAILLE LINE:  'slider Application Slider Frame Some slider: 0.0 Slider'",
     "     VISIBLE:  'Some slider: 0.0 Slider', cursor=1",
     "SPEECH OUTPUT: '0.0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Slider Where Am I",
    ["BRAILLE LINE:  'slider Application Slider Frame Some slider: 0.0 Slider'",
     "     VISIBLE:  'Some slider: 0.0 Slider', cursor=1",
     "SPEECH OUTPUT: 'Some slider: slider 0.0 0 percent Alt s'"]))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
