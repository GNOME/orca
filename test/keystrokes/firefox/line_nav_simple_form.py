#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with a simple
form.  
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

sequence.append(TypeAction(utils.htmlURLPrefix + "simpleform.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus(utils.htmlURLPrefix + "simpleform.html",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Type something here:  $l'",
     "     VISIBLE:  'Type something here:  $l', cursor=1",
     "SPEECH OUTPUT: 'Type something here: text'"]))

########################################################################
# Down Arrow to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. line Down",
    ["BRAILLE LINE:  'Magic disappearing text trick: tab to me and I disappear $l'",
     "     VISIBLE:  'Magic disappearing text trick: t', cursor=1",
     "SPEECH OUTPUT: 'Magic disappearing text trick: text tab to me and I disappear'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  'Tell me a secret:  $l'",
     "     VISIBLE:  'Tell me a secret:  $l', cursor=1",
     "SPEECH OUTPUT: 'Tell me a secret: password'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'Tell me a little more about yourself:'",
     "     VISIBLE:  'Tell me a little more about your', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  'I am a monkey with a long tail.  I like  $l'",
     "     VISIBLE:  'I am a monkey with a long tail. ', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself: text I am a monkey with a long tail.  I like'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. line Down",
    ["BRAILLE LINE:  'to swing from trees and eat bananas.   $l'",
     "     VISIBLE:  'to swing from trees and eat bana', cursor=1",
     "SPEECH OUTPUT: 'to swing from trees and eat bananas.  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. line Down",
    ["BRAILLE LINE:  'I've recently taken up typing and plan to  $l'",
     "     VISIBLE:  'I've recently taken up typing an', cursor=1",
     "SPEECH OUTPUT: 'I've recently taken up typing and plan to '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BRAILLE LINE:  'write my memoirs. $l'",
     "     VISIBLE:  'write my memoirs. $l', cursor=1",
     "SPEECH OUTPUT: 'write my memoirs.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  '      $l'",
     "     VISIBLE:  '      $l', cursor=1",
     "SPEECH OUTPUT: '     '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  '      $l'",
     "     VISIBLE:  '      $l', cursor=6",
     "SPEECH OUTPUT: '     '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  'Check one or more: < > CheckBox Red < > CheckBox Blue < > CheckBox Green'",
     "     VISIBLE:  'Check one or more: < > CheckBox ', cursor=1",
     "SPEECH OUTPUT: 'Check one or more: Red check box not checked Blue check box not checked Green check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  'Make a selection: Water Combo'",
     "     VISIBLE:  'Make a selection: Water Combo', cursor=1",
     "SPEECH OUTPUT: 'Make a selection: Water combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BRAILLE LINE:  'Which sports do you like?'",
     "     VISIBLE:  'Which sports do you like?', cursor=1",
     "SPEECH OUTPUT: 'Which sports do you like?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. line Down",
    ["BRAILLE LINE:  'Hockey List'",
     "     VISIBLE:  'Hockey List', cursor=1",
     "SPEECH OUTPUT: 'Hockey multi-select List with 4 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. line Down",
    ["BRAILLE LINE:  'Dashing picture of Willie Walker Image'",
     "     VISIBLE:  'Dashing picture of Willie Walker', cursor=1",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker image ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. line Down",
    ["BRAILLE LINE:  'Ain't he handsome (please say yes)? & y RadioButton Yes & y RadioButton No'",
     "     VISIBLE:  'Ain't he handsome (please say ye', cursor=1",
     "SPEECH OUTPUT: 'Ain't he handsome (please say yes)? not selected radio button Yes not selected radio button No'"]))

########################################################################
# Up Arrow to the Top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. line Up",
    ["BRAILLE LINE:  'Dashing picture of Willie Walker Image'",
     "     VISIBLE:  'Dashing picture of Willie Walker', cursor=1",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker image ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. line Up",
    ["BRAILLE LINE:  'Hockey List'",
     "     VISIBLE:  'Hockey List', cursor=1",
     "SPEECH OUTPUT: 'Hockey multi-select List with 4 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. line Up",
    ["BRAILLE LINE:  'Which sports do you like?'",
     "     VISIBLE:  'Which sports do you like?', cursor=1",
     "SPEECH OUTPUT: 'Which sports do you like?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. line Up",
    ["BRAILLE LINE:  'Make a selection: Water Combo'",
     "     VISIBLE:  'Make a selection: Water Combo', cursor=1",
     "SPEECH OUTPUT: 'Make a selection: Water combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. line Up",
    ["BRAILLE LINE:  'Check one or more: < > CheckBox Red < > CheckBox Blue < > CheckBox Green'",
     "     VISIBLE:  'Check one or more: < > CheckBox ', cursor=1",
     "SPEECH OUTPUT: 'Check one or more: Red check box not checked Blue check box not checked Green check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. line Up",
    ["BRAILLE LINE:  '      $l'",
     "     VISIBLE:  '      $l', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. line Up",
    ["BRAILLE LINE:  'write my memoirs. $l'",
     "     VISIBLE:  'write my memoirs. $l', cursor=1",
     "SPEECH OUTPUT: 'write my memoirs.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. line Up",
    ["BRAILLE LINE:  'I've recently taken up typing and plan to  $l'",
     "     VISIBLE:  'I've recently taken up typing an', cursor=1",
     "SPEECH OUTPUT: 'I've recently taken up typing and plan to '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. line Up",
    ["BRAILLE LINE:  'to swing from trees and eat bananas.   $l'",
     "     VISIBLE:  'to swing from trees and eat bana', cursor=1",
     "SPEECH OUTPUT: 'to swing from trees and eat bananas.  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. line Up",
    ["BRAILLE LINE:  'I am a monkey with a long tail.  I like  $l'",
     "     VISIBLE:  'I am a monkey with a long tail. ', cursor=1",
     "SPEECH OUTPUT: 'I am a monkey with a long tail.  I like '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. line Up",
    ["BRAILLE LINE:  'Tell me a little more about yourself:'",
     "     VISIBLE:  'Tell me a little more about your', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. line Up",
    ["BRAILLE LINE:  'Tell me a secret:  $l'",
     "     VISIBLE:  'Tell me a secret:  $l', cursor=1",
     "SPEECH OUTPUT: 'Tell me a secret: password'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. line Up",
    ["BRAILLE LINE:  'Magic disappearing text trick: tab to me and I disappear $l'",
     "     VISIBLE:  'Magic disappearing text trick: t', cursor=1",
     "SPEECH OUTPUT: 'Magic disappearing text trick: text tab to me and I disappear'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. line Up",
    ["BRAILLE LINE:  'Type something here:  $l'",
     "     VISIBLE:  'Type something here:  $l', cursor=1",
     "SPEECH OUTPUT: 'Type something here: text'"]))

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
