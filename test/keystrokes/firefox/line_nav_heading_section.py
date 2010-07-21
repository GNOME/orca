# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with headings
in sections.
"""

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

sequence.append(TypeAction(utils.htmlURLPrefix + "heading-section.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("HTML test page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Heading 1. h1'",
     "     VISIBLE:  'Heading 1. h1', cursor=1",
     "BRAILLE LINE:  'Heading 1. h1'",
     "     VISIBLE:  'Heading 1. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 1. heading level 1'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Heading 2. h1'",
     "     VISIBLE:  'Heading 2. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 2. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'sect 1'",
     "     VISIBLE:  'sect 1', cursor=1",
     "SPEECH OUTPUT: 'sect 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Heading 3. h1'",
     "     VISIBLE:  'Heading 3. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 3. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'sect 2'",
     "     VISIBLE:  'sect 2', cursor=1",
     "SPEECH OUTPUT: 'sect 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Heading 4. h1'",
     "     VISIBLE:  'Heading 4. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 4. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'sect 3'",
     "     VISIBLE:  'sect 3', cursor=1",
     "SPEECH OUTPUT: 'sect 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Heading 5. h1'",
     "     VISIBLE:  'Heading 5. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 5. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Heading 6. h1'",
     "     VISIBLE:  'Heading 6. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 6. heading level 1'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Heading 5. h1'",
     "     VISIBLE:  'Heading 5. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 5. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'sect 3'",
     "     VISIBLE:  'sect 3', cursor=1",
     "SPEECH OUTPUT: 'sect 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Heading 4. h1'",
     "     VISIBLE:  'Heading 4. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 4. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'sect 2'",
     "     VISIBLE:  'sect 2', cursor=1",
     "SPEECH OUTPUT: 'sect 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Heading 3. h1'",
     "     VISIBLE:  'Heading 3. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 3. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'sect 1'",
     "     VISIBLE:  'sect 1', cursor=1",
     "SPEECH OUTPUT: 'sect 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Heading 2. h1'",
     "     VISIBLE:  'Heading 2. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 2. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Heading 1. h1'",
     "     VISIBLE:  'Heading 1. h1', cursor=1",
     "SPEECH OUTPUT: 'Heading 1. heading level 1'"]))

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
