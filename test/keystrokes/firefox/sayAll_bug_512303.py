# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll on the problem document from bug 512303."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "table-caption.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Below is a table, with some sample table data'",
     "     VISIBLE:  'Below is a table, with some samp', cursor=1",
     "SPEECH OUTPUT: 'Below is a table, with some sample table data'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Below is a table, with some sample table data'",
     "SPEECH OUTPUT: 'this is a caption for this table caption'",
     "SPEECH OUTPUT: 'col1 column header'",
     "SPEECH OUTPUT: 'col2 column header'",
     "SPEECH OUTPUT: 'col3 column header'",
     "SPEECH OUTPUT: '1'",
     "SPEECH OUTPUT: '2'",
     "SPEECH OUTPUT: '3'",
     "SPEECH OUTPUT: '4'",
     "SPEECH OUTPUT: '5'",
     "SPEECH OUTPUT: '6'",
     "SPEECH OUTPUT: '7'",
     "SPEECH OUTPUT: '8'",
     "SPEECH OUTPUT: '9'",
     "SPEECH OUTPUT: 'hope the table looks pretty'"]))

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
