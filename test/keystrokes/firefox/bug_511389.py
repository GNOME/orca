#!/usr/bin/python

"""Test of the fix for bug 511389."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# Load the local test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction(utils.htmlURLPrefix + "bug-511389.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Hello world, this is a test.'",
     "     VISIBLE:  'Hello world, this is a test.', cursor=1",
     "SPEECH OUTPUT: 'Hello world'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ', this is a test.'"]))

########################################################################
# Down Arrow to the link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link'"]))

########################################################################
# Tab forward.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab",
    ["BRAILLE LINE:  'Bar'",
     "     VISIBLE:  'Bar', cursor=1",
     "SPEECH OUTPUT: 'Bar'",
     "SPEECH OUTPUT: 'link'"]))

########################################################################
# Shift+Tab back.  The bug was that we weren't speaking the link in
# this instance.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link'"]))

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
