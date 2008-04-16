# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of the fix for bug 511389."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

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
    ["BRAILLE LINE:  'Hello world Link , this is a test.'",
     "     VISIBLE:  'Hello world Link , this is a tes', cursor=1",
     "SPEECH OUTPUT: 'Hello world link , this is a test.'"]))

########################################################################
# Down Arrow to the link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Foo Link'",
     "     VISIBLE:  'Foo Link', cursor=1",
     "SPEECH OUTPUT: 'Foo link ",
     "'"]))

########################################################################
# Tab forward.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab",
    ["BRAILLE LINE:  'Bar Link'",
     "     VISIBLE:  'Bar Link', cursor=1",
     "BRAILLE LINE:  'Bar Link'",
     "     VISIBLE:  'Bar Link', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bar link'"]))

########################################################################
# Shift+Tab back.  The bug was that we weren't speaking the link in
# this instance.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab",
    ["BRAILLE LINE:  'Foo Link'",
     "     VISIBLE:  'Foo Link', cursor=1",
     "BRAILLE LINE:  'Foo Link'",
     "     VISIBLE:  'Foo Link', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Foo link'"]))

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
