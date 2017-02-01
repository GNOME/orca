#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Nest all the things!'",
     "     VISIBLE:  'Nest all the things!', cursor=1",
     "SPEECH OUTPUT: 'Nest all the things!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Hello world'",
     "     VISIBLE:  'Hello world', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: 'Hello world.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Nested item'",
     "     VISIBLE:  'Nested item', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: 'Nested item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Even-more-nested item'",
     "     VISIBLE:  'Even-more-nested item', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: 'Even-more-nested item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Is this seriously necessary?'",
     "     VISIBLE:  'Is this seriously necessary?', cursor=1",
     "SPEECH OUTPUT: 'List with 1 item.'",
     "SPEECH OUTPUT: 'Nesting level 3'",
     "SPEECH OUTPUT: 'Is this seriously necessary?.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Because why not?'",
     "     VISIBLE:  'Because why not?', cursor=1",
     "SPEECH OUTPUT: 'Leaving 4 lists.'",
     "SPEECH OUTPUT: 'Because why not?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Here's a quote'",
     "     VISIBLE:  'Here's a quote', cursor=1",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Here's a quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'A nested quote'",
     "     VISIBLE:  'A nested quote', cursor=1",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: 'A nested quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Containing a quote'",
     "     VISIBLE:  'Containing a quote', cursor=1",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: 'Containing a quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Which contains a quote'",
     "     VISIBLE:  'Which contains a quote', cursor=1",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Nesting level 3'",
     "SPEECH OUTPUT: 'Which contains a quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'Just... one... more... thing!'",
     "     VISIBLE:  'Just... one... more... thing!', cursor=1",
     "SPEECH OUTPUT: 'Leaving 3 blockquotes.'",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Just... one... more... thing!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'The end.'",
     "     VISIBLE:  'The end.', cursor=1",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'The end.'"]))


sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'Just... one... more... thing!'",
     "     VISIBLE:  'Just... one... more... thing!', cursor=1",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Just... one... more... thing!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'Which contains a quote'",
     "     VISIBLE:  'Which contains a quote', cursor=1",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Nesting level 3'",
     "SPEECH OUTPUT: 'Which contains a quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'Containing a quote'",
     "     VISIBLE:  'Containing a quote', cursor=1",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: 'Containing a quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'A nested quote'",
     "     VISIBLE:  'A nested quote', cursor=1",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: 'A nested quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  'Here's a quote'",
     "     VISIBLE:  'Here's a quote', cursor=1",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Here's a quote'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  'Because why not?'",
     "     VISIBLE:  'Because why not?', cursor=1",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'Because why not?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  'Is this seriously necessary?'",
     "     VISIBLE:  'Is this seriously necessary?', cursor=1",
     "SPEECH OUTPUT: 'List with 1 item.'",
     "SPEECH OUTPUT: 'Nesting level 3'",
     "SPEECH OUTPUT: 'Is this seriously necessary?.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  'Even-more-nested item'",
     "     VISIBLE:  'Even-more-nested item', cursor=1",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: 'Nesting level 2'",
     "SPEECH OUTPUT: 'Even-more-nested item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  'Nested item'",
     "     VISIBLE:  'Nested item', cursor=1",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: 'Nesting level 1'",
     "SPEECH OUTPUT: 'Nested item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Up",
    ["BRAILLE LINE:  'Hello world'",
     "     VISIBLE:  'Hello world', cursor=1",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: 'Hello world.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Up",
    ["BRAILLE LINE:  'Nest all the things!'",
     "     VISIBLE:  'Nest all the things!', cursor=1",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'Nest all the things!'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
