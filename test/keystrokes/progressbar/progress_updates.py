#!/usr/bin/python

"""Test of progressbar output using custom program.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and flat review to the progress bar
#
sequence.append(WaitForWindowActivate("ProgressBar"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyComboAction("KP_7"))

########################################################################
# Now, invoke the demo.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_PROGRESS_BAR,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Progress bar updates",
    ["BRAILLE LINE:  'Progress 10% $l'",
     "     VISIBLE:  'Progress 10% $l', cursor=1",
     "BRAILLE LINE:  'Progress 20% $l'",
     "     VISIBLE:  'Progress 20% $l', cursor=1",
     "BRAILLE LINE:  'Progress 30% $l'",
     "     VISIBLE:  'Progress 30% $l', cursor=1",
     "BRAILLE LINE:  'Progress 40% $l'",
     "     VISIBLE:  'Progress 40% $l', cursor=1",
     "BRAILLE LINE:  'Progress 50% $l'",
     "     VISIBLE:  'Progress 50% $l', cursor=1",
     "BRAILLE LINE:  'Progress 60% $l'",
     "     VISIBLE:  'Progress 60% $l', cursor=1",
     "BRAILLE LINE:  'Progress 70% $l'",
     "     VISIBLE:  'Progress 70% $l', cursor=1",
     "BRAILLE LINE:  'Progress 80% $l'",
     "     VISIBLE:  'Progress 80% $l', cursor=1",
     "BRAILLE LINE:  'Progress 90% $l'",
     "     VISIBLE:  'Progress 90% $l', cursor=1",
     "BRAILLE LINE:  'Progress 100% $l'",
     "     VISIBLE:  'Progress 100% $l', cursor=1",
     "SPEECH OUTPUT: '10 percent. '",
     "SPEECH OUTPUT: '20 percent. '",
     "SPEECH OUTPUT: '30 percent. '",
     "SPEECH OUTPUT: '40 percent. '",
     "SPEECH OUTPUT: '50 percent. '",
     "SPEECH OUTPUT: '60 percent. '",
     "SPEECH OUTPUT: '70 percent. '",
     "SPEECH OUTPUT: '80 percent. '",
     "SPEECH OUTPUT: '90 percent. '",
     "SPEECH OUTPUT: '100 percent. '"]))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
