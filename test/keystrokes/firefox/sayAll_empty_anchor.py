# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output of Firefox on a page with empty anchors."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "bug-517371" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-517371.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Testing",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'FAQ h1'",
     "     VISIBLE:  'FAQ h1', cursor=1",
     "SPEECH OUTPUT: 'FAQ '",
     "SPEECH OUTPUT: 'heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'FAQ '",
     "SPEECH OUTPUT: 'heading  '",
     "SPEECH OUTPUT: 'level 1'",
     "SPEECH OUTPUT: 'Battery heading  '",
     "SPEECH OUTPUT: 'level 2'",
     "SPEECH OUTPUT: 'Q. What's a battery? link'",
     "SPEECH OUTPUT: 'Q. Which way is up? link'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page? link'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: '",
     "FOO'",
     "SPEECH OUTPUT: 'heading  '",
     "SPEECH OUTPUT: 'level 2'",
     "SPEECH OUTPUT: 'Q. Why would someone put a line break in a heading? link'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Q. What is the airspeed velocity of an unladen swallow? link'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: '",
     "Battery heading  '",
     "SPEECH OUTPUT: 'level 2'",
     "SPEECH OUTPUT: 'Q. What is a battery?",
     "A. Look it up.'",
     "SPEECH OUTPUT: 'Q. Which way is up?",
     "A. That way.'",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?",
     "A. Empty anchors.'"]))

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
