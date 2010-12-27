# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of HTML list output of Firefox, in particular where am I.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local lists test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "lists2.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Lists Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  '•Not in a paragraph'",
     "     VISIBLE:  '•Not in a paragraph', cursor=1",
     "SPEECH OUTPUT: '•Not in a paragraph'"]))

########################################################################
# Press Down Arrow to move through the lists doing a where am I for each
# list item.
#
sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "1. Basic Where Am I",
    ["BRAILLE LINE:  '• In a paragraph'",
     "     VISIBLE:  '• In a paragraph', cursor=1",
     "SPEECH OUTPUT: 'list item • In a paragraph 2 of 4'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  '• In a section'",
     "     VISIBLE:  '• In a section', cursor=1",
     "SPEECH OUTPUT: 'list item • In a section 3 of 4'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["BRAILLE LINE:  '1.A nested list item, not in a paragraph'",
     "     VISIBLE:  '1.A nested list item, not in a p', cursor=1",
     "SPEECH OUTPUT: 'list item 1.A nested list item, not in a paragraph 1 of 3 Nesting level 1'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "4. Basic Where Am I",
    ["BRAILLE LINE:  '2. A nested list item, in a paragraph'",
     "     VISIBLE:  '2. A nested list item, in a para', cursor=1",
     "SPEECH OUTPUT: 'list item 2. A nested list item, in a paragraph 2 of 3 Nesting level 1'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "5. Basic Where Am I",
    ["BRAILLE LINE:  '3. A nested list item, in a section'",
     "     VISIBLE:  '3. A nested list item, in a sect', cursor=1",
     "SPEECH OUTPUT: 'list item 3. A nested list item, in a section 3 of 3 Nesting level 1'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "6. Basic Where Am I",
    ["BRAILLE LINE:  '• In a paragraph that's in a section'",
     "     VISIBLE:  '• In a paragraph that's in a sec', cursor=1",
     "SPEECH OUTPUT: 'list item • In a paragraph that's in a section 4 of 4'"]))

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
