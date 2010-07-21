# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of table structural navigation with headings which contain
anchors."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local blockquote test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-591592.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(3000))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'This is a test. h1'",
     "     VISIBLE:  'This is a test. h1', cursor=1",
     "SPEECH OUTPUT: 'This is a test. heading level 1'"]))

########################################################################
# Press h to move amongst the headings
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "1. h",
    ["BRAILLE LINE:  'Adding IPS Repositories h2'",
     "     VISIBLE:  'Adding IPS Repositories h2', cursor=1",
     "SPEECH OUTPUT: 'Adding IPS Repositories heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "2. h",
    ["BRAILLE LINE:  'Other Repositories h3'",
     "     VISIBLE:  'Other Repositories h3', cursor=1",
     "SPEECH OUTPUT: 'Other Repositories heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "3. h",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'This is a test. h1'",
     "     VISIBLE:  'This is a test. h1', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'This is a test. heading level 1'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
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
