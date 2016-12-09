#!/usr/bin/python

"""Test of object navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of File",
    ["BRAILLE LINE:  'Type something here:'",
     "     VISIBLE:  'Type something here:', cursor=1",
     "SPEECH OUTPUT: 'Type something here:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'Magic disappearing text trick:'",
     "     VISIBLE:  'Magic disappearing text trick:', cursor=1",
     "SPEECH OUTPUT: 'Magic disappearing text trick:"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. line Down",
    ["BRAILLE LINE:  'Tell me a secret:'",
     "     VISIBLE:  'Tell me a secret:', cursor=1",
     "SPEECH OUTPUT: 'Tell me a secret:"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'password text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BRAILLE LINE:  'Tell me a little more about yourself:'",
     "     VISIBLE:  'Tell me a little more about your', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  'I am a monkey with a long tail.  I like  $l'",
     "     VISIBLE:  'I am a monkey with a long tail. ', cursor=1",
     "SPEECH OUTPUT: 'entry I am a monkey with a long tail.  I like .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  'to swing from trees and eat bananas.   $l'",
     "     VISIBLE:  'to swing from trees and eat bana', cursor=1",
     "SPEECH OUTPUT: 'to swing from trees and eat bananas.  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  'I've recently taken up typing and plan to  $l'",
     "     VISIBLE:  'I've recently taken up typing an', cursor=1",
     "SPEECH OUTPUT: 'I've recently taken up typing and plan to .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  'write my memoirs. $l'",
     "     VISIBLE:  'write my memoirs. $l', cursor=1",
     "SPEECH OUTPUT: 'write my memoirs.",
     ".'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BRAILLE LINE:  'Check one or more:'",
     "     VISIBLE:  'Check one or more:', cursor=1",
     "SPEECH OUTPUT: 'Check one or more:"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. line Down",
    ["BRAILLE LINE:  '< > Red check box'",
     "     VISIBLE:  '< > Red check box', cursor=1",
     "SPEECH OUTPUT: 'Red check box not checked"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. line Down",
    ["BRAILLE LINE:  'Red'",
     "     VISIBLE:  'Red', cursor=1",
     "SPEECH OUTPUT: 'Red"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. line Down",
    ["BRAILLE LINE:  '< > Blue check box'",
     "     VISIBLE:  '< > Blue check box', cursor=1",
     "SPEECH OUTPUT: 'Blue check box not checked"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. line Down",
    ["BRAILLE LINE:  'Blue'",
     "     VISIBLE:  'Blue', cursor=1",
     "SPEECH OUTPUT: 'Blue"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. line Down",
    ["BRAILLE LINE:  '< > Green check box'",
     "     VISIBLE:  '< > Green check box', cursor=1",
     "SPEECH OUTPUT: 'Green check box not checked"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. line Down",
    ["BRAILLE LINE:  'Green'",
     "     VISIBLE:  'Green', cursor=1",
     "SPEECH OUTPUT: 'Green"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. line Down",
    ["BRAILLE LINE:  'Make a selection:'",
     "     VISIBLE:  'Make a selection:', cursor=1",
     "SPEECH OUTPUT: 'Make a selection:"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. line Down",
    ["BRAILLE LINE:  'Water combo box'",
     "     VISIBLE:  'Water combo box', cursor=1",
     "SPEECH OUTPUT: 'Water combo box"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. line Down",
    ["BRAILLE LINE:  'Which sports do you like?'",
     "     VISIBLE:  'Which sports do you like?', cursor=1",
     "SPEECH OUTPUT: 'Which sports do you like?"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 4 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. line Down",
    ["BRAILLE LINE:  'Dashing picture of Willie Walker image'",
     "     VISIBLE:  'Dashing picture of Willie Walker', cursor=1",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker image"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. line Down",
    ["BRAILLE LINE:  'Ain't he handsome (please say yes)?'",
     "     VISIBLE:  'Ain't he handsome (please say ye', cursor=1",
     "SPEECH OUTPUT: 'Ain't he handsome (please say yes)?"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "25. line Down",
    ["BRAILLE LINE:  '& y Yes radio button'",
     "     VISIBLE:  '& y Yes radio button', cursor=1",
     "SPEECH OUTPUT: 'Yes.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "26. line Down",
    ["BRAILLE LINE:  'Yes'",
     "     VISIBLE:  'Yes', cursor=1",
     "SPEECH OUTPUT: 'Yes'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "27. line Down",
    ["BRAILLE LINE:  '& y No radio button'",
     "     VISIBLE:  '& y No radio button', cursor=1",
     "SPEECH OUTPUT: 'No.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "28. line Down",
    ["BRAILLE LINE:  'No'",
     "     VISIBLE:  'No', cursor=1",
     "SPEECH OUTPUT: 'No'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
