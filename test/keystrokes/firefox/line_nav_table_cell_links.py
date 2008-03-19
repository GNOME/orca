# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with links
in a table cell with line breaks.
"""

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

sequence.append(TypeAction(utils.htmlURLPrefix + "table-cell-links.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Table Cell Links",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Here are some links'",
     "     VISIBLE:  'Here are some links', cursor=1",
     "SPEECH OUTPUT: 'Here are some links'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'HTML Tags'",
     "     VISIBLE:  'HTML Tags', cursor=1",
     "SPEECH OUTPUT: 'HTML Tags",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<!--> Link'",
     "     VISIBLE:  '<!--> Link', cursor=1",
     "SPEECH OUTPUT: '<!--> link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<!DOCTYPE> Link'",
     "     VISIBLE:  '<!DOCTYPE> Link', cursor=1",
     "SPEECH OUTPUT: '<!DOCTYPE> link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<a> Link '",
     "     VISIBLE:  '<a> Link ', cursor=1",
     "SPEECH OUTPUT: '<a> link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<abbr> Link '",
     "     VISIBLE:  '<abbr> Link ', cursor=1",
     "SPEECH OUTPUT: '<abbr> link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<acronym> Link'",
     "     VISIBLE:  '<acronym> Link', cursor=1",
     "SPEECH OUTPUT: '<acronym> link'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<abbr> Link '",
     "     VISIBLE:  '<abbr> Link ', cursor=1",
     "SPEECH OUTPUT: '<abbr> link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<a> Link '",
     "     VISIBLE:  '<a> Link ', cursor=1",
     "SPEECH OUTPUT: '<a> link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<!DOCTYPE> Link'",
     "     VISIBLE:  '<!DOCTYPE> Link', cursor=1",
     "SPEECH OUTPUT: '<!DOCTYPE> link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<!--> Link'",
     "     VISIBLE:  '<!--> Link', cursor=1",
     "SPEECH OUTPUT: '<!--> link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'HTML Tags'",
     "     VISIBLE:  'HTML Tags', cursor=1",
     "SPEECH OUTPUT: 'HTML Tags",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Here are some links'",
     "     VISIBLE:  'Here are some links', cursor=1",
     "SPEECH OUTPUT: 'Here are some links'"]))

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
