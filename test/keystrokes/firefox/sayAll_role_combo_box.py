#!/usr/bin/python

"""Test of sayAll output on a page with HTML combo boxes in Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local combo box test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "combobox.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Combo Box Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Severity: Severity normal Combo'",
     "     VISIBLE:  'Severity: Severity normal Combo', cursor=1",
     "SPEECH OUTPUT: 'Severity link : Severity normal combo box'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Severity link'",
     "SPEECH OUTPUT: ': Severity normal combo box'",
     "SPEECH OUTPUT: 'Priority link'",
     "SPEECH OUTPUT: ': Normal combo box'",
     "SPEECH OUTPUT: 'Resolution: ", 
     "'",
     "SPEECH OUTPUT: 'FIXED'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'Version'",
     "SPEECH OUTPUT: '2.16 combo box'",
     "SPEECH OUTPUT: 'Component'",
     "SPEECH OUTPUT: 'Speech combo box'"]))

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
