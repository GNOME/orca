# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output of Firefox on a page with nested layout tables."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "nested-tables.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Nested Tables",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'nested-tables link image'",
     "SPEECH OUTPUT: 'Campus link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Classroom link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Communicate link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Reports link'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Your Learning Plan'",
     "SPEECH OUTPUT: 'Below is a list of the courses that make up your learning plan.  '",
     "SPEECH OUTPUT: 'UNIX 2007'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Take Course link'",
     "SPEECH OUTPUT: 'You have completed 87 of the 87 modules in this course.'",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'SQL Plus'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Take Course link'",
     "SPEECH OUTPUT: 'You have completed 59 of the 184 modules in this course.'",
     "SPEECH OUTPUT: 'separator'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
