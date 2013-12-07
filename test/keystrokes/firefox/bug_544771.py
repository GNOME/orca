#!/usr/bin/python

"""Test of navigation to same page links.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# Load the local test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction(utils.htmlURLPrefix + "bug-544771.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Contents h1'",
     "     VISIBLE:  'Contents h1', cursor=1",
     "SPEECH OUTPUT: 'Contents'",
     "SPEECH OUTPUT: 'heading level 1'"]))

########################################################################
# Press Tab twice to move to the Second link. Then press Return. Down
# Arrow to verify we've updated our position.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab", 
    ["BRAILLE LINE:  '\u2022First item'",
     "     VISIBLE:  '\u2022First item', cursor=2",
     "SPEECH OUTPUT: 'First item'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab", 
    ["BRAILLE LINE:  '\u2022Second item'",
     "     VISIBLE:  '\u2022Second item', cursor=2",
     "SPEECH OUTPUT: 'Second item'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Return", 
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down", 
    ["BRAILLE LINE:  'Second h2'",
     "     VISIBLE:  'Second h2', cursor=1",
     "SPEECH OUTPUT: 'Second heading'",
     "SPEECH OUTPUT: 'heading level 2'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
