# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with nested
layout tables. 
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

sequence.append(TypeAction(utils.htmlURLPrefix + "nested-tables.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Nested Tables",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BUG? - We're missing the initial line of links",
     "BRAILLE LINE:  'nested-tables Link Image Your Learning Plan'",
     "     VISIBLE:  'nested-tables Link Image Your Le', cursor=0",
     "SPEECH OUTPUT: 'nested-tables link image Your Learning Plan'"]))

########################################################################
# Down Arrow to the End.
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(utils.AssertPresentationAction(
#    "1. line Down",
#    ["BRAILLE LINE:  'Campus Link   .   Classroom Link   .   Communicate Link   .   Reports Link  '",
#     "     VISIBLE:  'Campus Link   .   Classroom ', cursor=1",
#     "SPEECH OUTPUT: 'Campus link   .   Classroom link   .   Communicate link   .   Reports link  '"]))
#
#sequence.append(utils.StartRecordingAction())
#sequence.append(KeyComboAction("Down"))
#sequence.append(utils.AssertPresentationAction(
#    "2. line Down",
#    ["BRAILLE LINE:  'Your Learning Plan'",
#     "     VISIBLE:  'Your Learning Plan', cursor=1",
#     "SPEECH OUTPUT: 'Your Learning Plan'"]))
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BUG? - For some reason we're repeating ourselves",
     "BRAILLE LINE:  'Below is a list of the courses that make up your learning plan.'",
     "     VISIBLE:  'Below is a list of the courses t', cursor=1",
     "BRAILLE LINE:  'Below is a list of the courses that make up your learning plan.'",
     "     VISIBLE:  'Below is a list of the courses t', cursor=1",
     "SPEECH OUTPUT: 'Below is a list of the courses that make up your learning plan.'",
     "SPEECH OUTPUT: 'Below is a list of the courses that make up your learning plan.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. line Down",
    ["BRAILLE LINE:  'UNIX 2007'",
     "     VISIBLE:  'UNIX 2007', cursor=1",
     "SPEECH OUTPUT: 'UNIX 2007'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. line Down",
    ["BRAILLE LINE:  'Take Course Link'",
     "     VISIBLE:  'Take Course Link', cursor=0",
     "SPEECH OUTPUT: '  Take Course link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BRAILLE LINE:  'You have completed 87 of the 87 modules in this course.'",
     "     VISIBLE:  'You have completed 87 of the 87 ', cursor=1",
     "SPEECH OUTPUT: 'You have completed 87 of the 87 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  'SQL Plus'",
     "     VISIBLE:  'SQL Plus', cursor=1",
     "SPEECH OUTPUT: 'SQL Plus'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  'Take Course Link'",
     "     VISIBLE:  'Take Course Link', cursor=0",
     "SPEECH OUTPUT: '  Take Course link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  'You have completed 59 of the 184 modules in this course.'",
     "     VISIBLE:  'You have completed 59 of the 184', cursor=1",
     "SPEECH OUTPUT: 'You have completed 59 of the 184 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

########################################################################
# Up Arrow to the Top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. line Up",
    ["BRAILLE LINE:  'You have completed 59 of the 184 modules in this course.'",
     "     VISIBLE:  'You have completed 59 of the 184', cursor=1",
     "SPEECH OUTPUT: 'You have completed 59 of the 184 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. line Up",
    ["BRAILLE LINE:  'Take Course Link'",
     "     VISIBLE:  'Take Course Link', cursor=0",
     "SPEECH OUTPUT: '  Take Course link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. line Up",
    ["BRAILLE LINE:  'SQL Plus'",
     "     VISIBLE:  'SQL Plus', cursor=1",
     "SPEECH OUTPUT: 'SQL Plus'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. line Up",
    ["BRAILLE LINE:  'You have completed 87 of the 87 modules in this course.'",
     "     VISIBLE:  'You have completed 87 of the 87 ', cursor=1",
     "SPEECH OUTPUT: 'You have completed 87 of the 87 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. line Up",
    ["BRAILLE LINE:  'Take Course Link'",
     "     VISIBLE:  'Take Course Link', cursor=0",
     "SPEECH OUTPUT: '  Take Course link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. line Up",
    ["BRAILLE LINE:  'UNIX 2007'",
     "     VISIBLE:  'UNIX 2007', cursor=1",
     "SPEECH OUTPUT: 'UNIX 2007'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. line Up",
    ["BRAILLE LINE:  'Below is a list of the courses that make up your learning plan.'",
     "     VISIBLE:  'Below is a list of the courses t', cursor=1",
     "SPEECH OUTPUT: 'Below is a list of the courses that make up your learning plan.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. line Up",
    ["BRAILLE LINE:  'Your Learning Plan'",
     "     VISIBLE:  'Your Learning Plan', cursor=1",
     "SPEECH OUTPUT: 'Your Learning Plan'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. line Up",
    ["BRAILLE LINE:  'Campus Link   . Classroom Link   . Communicate Link   . Reports Link'",
     "     VISIBLE:  'Campus Link   . Classroom Link', cursor=1",
     "SPEECH OUTPUT: 'Campus link   .   Classroom link   .   Communicate link   .   Reports link  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. line Up",
    ["BRAILLE LINE:  'nested-tables Link Image'",
     "     VISIBLE:  'nested-tables Link Image', cursor=1",
     "SPEECH OUTPUT: 'nested-tables link image'"]))

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
