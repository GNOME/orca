#!/usr/bin/python

"""Test for the fix of bug 589455"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# Load the local test case
#
sequence.append(KeyComboAction("<Control>l"))
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
    ["BRAILLE LINE:  '1.Anchors2.html h3'",
     "     VISIBLE:  '1.Anchors2.html h3', cursor=3",
     "SPEECH OUTPUT: 'Anchors2.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'heading level 3'"]))

########################################################################
# Press Return to activate the link which should have focus.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Press Return to active the link",
    ["BRAILLE LINE:  'Finished loading Links to test files.'",
     "     VISIBLE:  'Finished loading Links to test f', cursor=0",
     "BRAILLE LINE:  'Here are some of our local test files:'",
     "     VISIBLE:  'Here are some of our local test ', cursor=1",
    "SPEECH OUTPUT: 'Finished loading Links to test files.' voice=system",
    "SPEECH OUTPUT: 'Here are some of our local test files:'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'anchors.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'blockquotes.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'bugzilla_top.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'combobox.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'fieldset.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'htmlpage.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'image-test.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'linebreak-test.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'lists.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'samesizearea.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'simpleform.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'simpleheader.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'slash-test.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'status-bar.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'tables.html link'",
    "SPEECH OUTPUT: '\u2022'",
    "SPEECH OUTPUT: 'textattributes.html link'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
