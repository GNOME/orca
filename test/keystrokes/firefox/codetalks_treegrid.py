# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of Codetalk's treegrid presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://codetalks.org/source/widgets/treegrid/treegrid.sample.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Navigate to the treegrid
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to the treegrid",
    ["KNOWN ISSUE - This output and the output of all the assertions that follow are merely designed to illustrate the current state of affairs, namely that Orca's caret navigation is not stomping on the built-in navigation of this treegrid, and to ensure that subsequent changes to Orca do not change that. This output should NOT be seen as what we think is an ideal presentation of a treegrid. See http://bugzilla.gnome.org/show_bug.cgi?id=570556 for more information.",
     "BRAILLE LINE:  '+A Question of Love+A Question of Love collapsed +A Question of Love'",
     "     VISIBLE:  '+A Question of Love collapsed +A', cursor=1",
     "SPEECH OUTPUT: 'Title tree table +A Question of Love'"]))

########################################################################
# Down Arrow to the next two items.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["BRAILLE LINE:  '+ Piece of Peace Cell'",
     "     VISIBLE:  '+ Piece of Peace Cell', cursor=1",
     "SPEECH OUTPUT: '+ Piece of Peace'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["BRAILLE LINE:  '+ International Law Cell'",
     "     VISIBLE:  '+ International Law Cell', cursor=1",
     "SPEECH OUTPUT: '+ International Law'"]))

########################################################################
# Up Arrow to the previous two items.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BRAILLE LINE:  '+ Piece of Peace Cell'",
     "     VISIBLE:  '+ Piece of Peace Cell', cursor=1",
     "SPEECH OUTPUT: '+ Piece of Peace'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BUG? - What's with the repetition in the braille? Might be a 4.0 issue?",
     "BRAILLE LINE:  '+A Question of Love+A Question of Love collapsed +A Question of Love'",
     "     VISIBLE:  '+A Question of Love collapsed +A', cursor=1",
     "SPEECH OUTPUT: '+A Question of Love'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  '+A Question of Love+A Question of Love collapsed +A Question of Love'",
     "     VISIBLE:  '+A Question of Love collapsed +A', cursor=1",
     "SPEECH OUTPUT: 'list item +A Question of Love'"]))

########################################################################
# Space to expand the current item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "Space to expand the current item", 
    ["BUG? - Why aren't we also speaking this?",
     "BRAILLE LINE:  '-A Question of Love-A Question of Love expanded -A Question of Love'",
     "     VISIBLE:  '-A Question of Love expanded -A ', cursor=1",
     "BRAILLE LINE:  '-A Question of Love-A Question of Love expanded -A Question of Love'",
     "     VISIBLE:  '-A Question of Love expanded -A ', cursor=1"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  '-A Question of Love-A Question of Love expanded -A Question of Love'",
     "     VISIBLE:  '-A Question of Love expanded -A ', cursor=1",
     "SPEECH OUTPUT: 'list item -A Question of Love'"]))

########################################################################
# Down Arrow to the child item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow into child", 
    ["BRAILLE LINE:  '978-3-453-40540-0 Cell Nora Roberts Cell $ 9.99 Cell'",
     "     VISIBLE:  '978-3-453-40540-0 Cell Nora Robe', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0'"]))

########################################################################
# Right Arrow in the child item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Right Arrow in child", 
    ["BRAILLE LINE:  '978-3-453-40540-0 Cell Nora Roberts Cell $ 9.99 Cell'",
     "     VISIBLE:  'Nora Roberts Cell $ 9.99 Cell', cursor=1",
     "SPEECH OUTPUT: 'Nora Roberts'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right Arrow in child", 
    ["BRAILLE LINE:  '978-3-453-40540-0 Cell Nora Roberts Cell $ 9.99 Cell'",
     "     VISIBLE:  '$ 9.99 Cell', cursor=1",
     "SPEECH OUTPUT: '$ 9.99'"]))

########################################################################
# Left Arrow in the child item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "1. Left Arrow in child", 
    ["BRAILLE LINE:  '978-3-453-40540-0 Cell Nora Roberts Cell $ 9.99 Cell'",
     "     VISIBLE:  'Nora Roberts Cell $ 9.99 Cell', cursor=1",
     "SPEECH OUTPUT: 'Nora Roberts'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Left Arrow in child", 
    ["BRAILLE LINE:  '978-3-453-40540-0 Cell Nora Roberts Cell $ 9.99 Cell'",
     "     VISIBLE:  '978-3-453-40540-0 Cell Nora Robe', cursor=1",
     "SPEECH OUTPUT: '978-3-453-40540-0'"]))

########################################################################
# Up Arrow back to parent item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow back to parent", 
    ["BRAILLE LINE:  '-A Question of Love-A Question of Love expanded -A Question of Love'",
     "     VISIBLE:  '-A Question of Love expanded -A ', cursor=1",
     "SPEECH OUTPUT: '-A Question of Love'"]))

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
