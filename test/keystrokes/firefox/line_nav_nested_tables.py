#!/usr/bin/python

"""Test of line navigation on a page with nested layout tables. """

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'nested-tables image'",
     "     VISIBLE:  'nested-tables image', cursor=0",
     "SPEECH OUTPUT: 'nested-tables'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  'Campus  .  Classroom  .  Communicate  .  Reports'",
     "     VISIBLE:  'Campus  .  Classroom  .  Communi', cursor=1",
     "SPEECH OUTPUT: 'Campus'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Classroom'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Communicate'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Reports'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'Your Learning Plan'",
     "     VISIBLE:  'Your Learning Plan', cursor=1",
     "SPEECH OUTPUT: 'Your Learning Plan'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  'Below is a list of the courses that make up your learning plan.'",
     "     VISIBLE:  'Below is a list of the courses t', cursor=1",
     "SPEECH OUTPUT: 'Below is a list of the courses that make up your learning plan. '"]))

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
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BRAILLE LINE:  'Take Course'",
     "     VISIBLE:  'Take Course', cursor=1",
     "SPEECH OUTPUT: 'Take Course'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  'You have completed 87 of the 87 modules in this course.'",
     "     VISIBLE:  'You have completed 87 of the 87 ', cursor=1",
     "SPEECH OUTPUT: 'You have completed 87 of the 87 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=0",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BRAILLE LINE:  'SQL Plus'",
     "     VISIBLE:  'SQL Plus', cursor=1",
     "SPEECH OUTPUT: 'SQL Plus'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. line Down",
    ["BRAILLE LINE:  'Take Course'",
     "     VISIBLE:  'Take Course', cursor=1",
     "SPEECH OUTPUT: 'Take Course'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. line Down",
    ["BRAILLE LINE:  'You have completed 59 of the 184 modules in this course.'",
     "     VISIBLE:  'You have completed 59 of the 184', cursor=1",
     "SPEECH OUTPUT: 'You have completed 59 of the 184 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=0",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. line Up",
    ["BRAILLE LINE:  'You have completed 59 of the 184 modules in this course.'",
     "     VISIBLE:  'You have completed 59 of the 184', cursor=1",
     "SPEECH OUTPUT: 'You have completed 59 of the 184 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. line Up",
    ["BRAILLE LINE:  'Take Course'",
     "     VISIBLE:  'Take Course', cursor=1",
     "SPEECH OUTPUT: 'Take Course'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. line Up",
    ["BRAILLE LINE:  'SQL Plus'",
     "     VISIBLE:  'SQL Plus', cursor=1",
     "SPEECH OUTPUT: 'SQL Plus'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. line Up",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=0",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. line Up",
    ["BRAILLE LINE:  'You have completed 87 of the 87 modules in this course.'",
     "     VISIBLE:  'You have completed 87 of the 87 ', cursor=1",
     "SPEECH OUTPUT: 'You have completed 87 of the 87 modules in this course.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. line Up",
    ["BRAILLE LINE:  'Take Course'",
     "     VISIBLE:  'Take Course', cursor=1",
     "SPEECH OUTPUT: 'Take Course'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. line Up",
    ["BRAILLE LINE:  'UNIX 2007'",
     "     VISIBLE:  'UNIX 2007', cursor=1",
     "SPEECH OUTPUT: 'UNIX 2007'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. line Up",
    ["BRAILLE LINE:  'Below is a list of the courses that make up your learning plan.'",
     "     VISIBLE:  'Below is a list of the courses t', cursor=1",
     "SPEECH OUTPUT: 'Below is a list of the courses that make up your learning plan. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. line Up",
    ["BRAILLE LINE:  'Your Learning Plan'",
     "     VISIBLE:  'Your Learning Plan', cursor=1",
     "SPEECH OUTPUT: 'Your Learning Plan'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. line Up",
    ["BRAILLE LINE:  'Campus  .  Classroom  .  Communicate  .  Reports'",
     "     VISIBLE:  'Campus  .  Classroom  .  Communi', cursor=1",
     "SPEECH OUTPUT: 'Campus'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Classroom'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Communicate'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '  .  '",
     "SPEECH OUTPUT: 'Reports'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. line Up",
    ["BRAILLE LINE:  'nested-tables image'",
     "     VISIBLE:  'nested-tables image', cursor=0",
     "SPEECH OUTPUT: 'nested-tables'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
