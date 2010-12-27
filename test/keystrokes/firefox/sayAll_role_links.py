# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output of a page consisting of mostly HTML links."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local anchors test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "anchors2.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Links to test files",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Here are some of our local test files:'",
     "     VISIBLE:  'Here are some of our local test ', cursor=1",
     "SPEECH OUTPUT: 'Here are some of our local test files:'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Here are some of our local test files:'",
     "SPEECH OUTPUT: '• anchors.html link'",
     "SPEECH OUTPUT: '• blockquotes.html link'",
     "SPEECH OUTPUT: '• bugzilla_top.html link'",
     "SPEECH OUTPUT: '• combobox.html link'",
     "SPEECH OUTPUT: '• fieldset.html link'",
     "SPEECH OUTPUT: '• htmlpage.html link'",
     "SPEECH OUTPUT: '• image-test.html link'",
     "SPEECH OUTPUT: '• linebreak-test.html link'",
     "SPEECH OUTPUT: '• lists.html link'",
     "SPEECH OUTPUT: '• samesizearea.html link'",
     "SPEECH OUTPUT: '• simpleform.html link'",
     "SPEECH OUTPUT: '• simpleheader.html link'",
     "SPEECH OUTPUT: '• slash-test.html link'",
     "SPEECH OUTPUT: '• status-bar.html link'",
     "SPEECH OUTPUT: '• tables.html link'",
     "SPEECH OUTPUT: '• textattributes.html link'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l", 1000))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
