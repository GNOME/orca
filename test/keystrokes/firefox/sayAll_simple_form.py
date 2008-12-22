#!/usr/bin/python

"""Test of sayAll output of Firefox on a page with a simple form."""

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

sequence.append(TypeAction(utils.htmlURLPrefix + "simpleform.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus(utils.htmlURLPrefix + "simpleform.html",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Type something here:  $l'",
     "     VISIBLE:  'Type something here:  $l', cursor=1",
     "SPEECH OUTPUT: 'Type something here: text'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Type something here: text'",
     "SPEECH OUTPUT: 'Magic disappearing text trick: text tab to me and I disappear'",
     "SPEECH OUTPUT: 'Tell me a secret: password'",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:",
     " text'",
     "SPEECH OUTPUT: 'Check one or more: Red check box not checked Blue check box not checked Green check box not checked'",
     "SPEECH OUTPUT: 'Make a selection: Water combo box'",
     "SPEECH OUTPUT: 'Which sports do you like?",
     " Hockey multi-select List with 4 items'",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker image'",
     "SPEECH OUTPUT: '",
     "Ain't he handsome (please say yes)? not selected radio button Yes not selected radio button No'"]))

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
