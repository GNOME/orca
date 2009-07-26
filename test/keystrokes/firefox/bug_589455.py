# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test for the fix of bug 589455
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Tab Panel Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "bug-589455.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Here is a result:'",
     "     VISIBLE:  'Here is a result:', cursor=1",
     "SPEECH OUTPUT: 'Here is a result:'"]))

########################################################################
# Press 3 to move to the heading at level 3, which happens to be a link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("3"))
sequence.append(utils.AssertPresentationAction(
    "Press 3 to move to the heading at level 3",
    ["BRAILLE LINE:  '1. Anchors2.html h3'",
     "     VISIBLE:  '1. Anchors2.html h3', cursor=4",
     "SPEECH OUTPUT: 'Anchors2.html link heading level 3'"]))

########################################################################
# Press Return to activate the link which should have focus.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Press Return to active the link",
    ["BRAILLE LINE:  'Loading.  Please wait.'",
     "     VISIBLE:  'Loading.  Please wait.', cursor=0",
     "BRAILLE LINE:  'Finished loading Links to test files.'",
     "     VISIBLE:  'Finished loading Links to test f', cursor=0",
     "BRAILLE LINE:  'Here are some of our local test files:'",
     "     VISIBLE:  'Here are some of our local test ', cursor=1",
     "BRAILLE LINE:  'Here are some of our local test files:'",
     "     VISIBLE:  'Here are some of our local test ', cursor=1",
     "SPEECH OUTPUT: 'Loading.  Please wait.'",
     "SPEECH OUTPUT: 'Finished loading Links to test files.'",
     "SPEECH OUTPUT: 'Here are some of our local test files:'",
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
     "SPEECH OUTPUT: '• textattributes.html link'",
     "SPEECH OUTPUT: 'Here are some of our local test files:'",
     "SPEECH OUTPUT: '100 percent'"]))

########################################################################
# Close the demo
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
