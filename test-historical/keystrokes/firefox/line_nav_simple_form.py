#!/usr/bin/python

"""Test of line navigation on a page with a simple form."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. line Down",
    ["BRAILLE LINE:  'Magic disappearing text trick: tab to me and I disappear $l'",
     "     VISIBLE:  'Magic disappearing text trick: t', cursor=1",
     "SPEECH OUTPUT: 'Magic disappearing text trick:'",
     "SPEECH OUTPUT: 'entry tab to me and I disappear.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  'Tell me a secret:  $l'",
     "     VISIBLE:  'Tell me a secret:  $l', cursor=1",
     "SPEECH OUTPUT: 'Tell me a secret:'",
     "SPEECH OUTPUT: 'password text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'Tell me a little more about yourself:'",
     "     VISIBLE:  'Tell me a little more about your', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  'I am a monkey with a long tail.  I like  $l'",
     "     VISIBLE:  'I am a monkey with a long tail. ', cursor=1",
     "SPEECH OUTPUT: 'entry I am a monkey with a long tail.  I like .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. line Down",
    ["BRAILLE LINE:  'to swing from trees and eat bananas.   $l'",
     "     VISIBLE:  'to swing from trees and eat bana', cursor=1",
     "SPEECH OUTPUT: 'to swing from trees and eat bananas.  .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. line Down",
    ["BRAILLE LINE:  'I've recently taken up typing and plan to  $l'",
     "     VISIBLE:  'I've recently taken up typing an', cursor=1",
     "SPEECH OUTPUT: 'I've recently taken up typing and plan to .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BRAILLE LINE:  'write my memoirs. $l'",
     "     VISIBLE:  'write my memoirs. $l', cursor=1",
     "SPEECH OUTPUT: 'write my memoirs.",
     ".'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  'Check one or more: < > Red check box < > Blue check box < > Green check box'",
     "     VISIBLE:  'Check one or more: < > Red check', cursor=1",
     "SPEECH OUTPUT: 'Check one or more:'",
     "SPEECH OUTPUT: 'Red check box not checked.'",
     "SPEECH OUTPUT: 'Blue check box not checked.'",
     "SPEECH OUTPUT: 'Green check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  'Make a selection: Water combo box'",
     "     VISIBLE:  'Make a selection: Water combo bo', cursor=1",
     "SPEECH OUTPUT: 'Make a selection:'",
     "SPEECH OUTPUT: 'Water combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  'Which sports do you like?'",
     "     VISIBLE:  'Which sports do you like?', cursor=1",
     "SPEECH OUTPUT: 'Which sports do you like?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 4 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BRAILLE LINE:  'Dashing picture of Willie Walker image'",
     "     VISIBLE:  'Dashing picture of Willie Walker', cursor=1",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. line Down",
    ["BRAILLE LINE:  'Ain't he handsome (please say yes)? & y Yes radio button Yes & y No radio button No'",
     "     VISIBLE:  'Ain't he handsome (please say ye', cursor=1",
     "SPEECH OUTPUT: 'Ain't he handsome (please say yes)?'",
     "SPEECH OUTPUT: 'Yes.'",
     "SPEECH OUTPUT: 'not selected radio button'",
     "SPEECH OUTPUT: 'Yes'",
     "SPEECH OUTPUT: 'No.'",
     "SPEECH OUTPUT: 'not selected radio button'",
     "SPEECH OUTPUT: 'No'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. line Up",
    ["BRAILLE LINE:  'Dashing picture of Willie Walker image'",
     "     VISIBLE:  'Dashing picture of Willie Walker', cursor=1",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. line Up",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 4 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. line Up",
    ["BRAILLE LINE:  'Which sports do you like?'",
     "     VISIBLE:  'Which sports do you like?', cursor=1",
     "SPEECH OUTPUT: 'Which sports do you like?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. line Up",
    ["BRAILLE LINE:  'Make a selection: Water combo box'",
     "     VISIBLE:  'Make a selection: Water combo bo', cursor=1",
     "SPEECH OUTPUT: 'Make a selection:'",
     "SPEECH OUTPUT: 'Water combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. line Up",
    ["BRAILLE LINE:  'Check one or more: < > Red check box < > Blue check box < > Green check box'",
     "     VISIBLE:  'Check one or more: < > Red check', cursor=1",
     "SPEECH OUTPUT: 'Check one or more:'",
     "SPEECH OUTPUT: 'Red check box not checked.'",
     "SPEECH OUTPUT: 'Blue check box not checked.'",
     "SPEECH OUTPUT: 'Green check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. line Up",
    ["BRAILLE LINE:  'write my memoirs. $l'",
     "     VISIBLE:  'write my memoirs. $l', cursor=1",
     "SPEECH OUTPUT: 'write my memoirs.",
     ".'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. line Up",
    ["BRAILLE LINE:  'I've recently taken up typing and plan to  $l'",
     "     VISIBLE:  'I've recently taken up typing an', cursor=1",
     "SPEECH OUTPUT: 'I've recently taken up typing and plan to .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. line Up",
    ["BRAILLE LINE:  'to swing from trees and eat bananas.   $l'",
     "     VISIBLE:  'to swing from trees and eat bana', cursor=1",
     "SPEECH OUTPUT: 'to swing from trees and eat bananas.  .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. line Up",
    ["BRAILLE LINE:  'I am a monkey with a long tail.  I like  $l'",
     "     VISIBLE:  'I am a monkey with a long tail. ', cursor=1",
     "SPEECH OUTPUT: 'I am a monkey with a long tail.  I like .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. line Up",
    ["BRAILLE LINE:  'Tell me a little more about yourself:'",
     "     VISIBLE:  'Tell me a little more about your', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. line Up",
    ["BRAILLE LINE:  'Tell me a secret:  $l'",
     "     VISIBLE:  'Tell me a secret:  $l', cursor=1",
     "SPEECH OUTPUT: 'Tell me a secret:'",
     "SPEECH OUTPUT: 'password text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. line Up",
    ["BRAILLE LINE:  'Magic disappearing text trick: tab to me and I disappear $l'",
     "     VISIBLE:  'Magic disappearing text trick: t', cursor=1",
     "SPEECH OUTPUT: 'Magic disappearing text trick:'",
     "SPEECH OUTPUT: 'entry tab to me and I disappear.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. line Up",
    ["BRAILLE LINE:  'Type something here:  $l'",
     "     VISIBLE:  'Type something here:  $l', cursor=1",
     "SPEECH OUTPUT: 'Type something here:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
