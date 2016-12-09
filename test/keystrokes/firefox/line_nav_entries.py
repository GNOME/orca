#!/usr/bin/python

"""Test of line navigation."""

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
    "1. Top of file",
    ["BRAILLE LINE:  'Here are some entries h2'",
     "     VISIBLE:  'Here are some entries h2', cursor=1",
     "SPEECH OUTPUT: 'Here are some entries heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  'Type something rather amusing he', cursor=1",
     "SPEECH OUTPUT: 'Type'",
     "SPEECH OUTPUT: 'something'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'rather'",
     "SPEECH OUTPUT: 'amusing'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'here:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Amusing numbers fall between  $l and  $l.'",
     "     VISIBLE:  'Amusing numbers fall between  $l', cursor=1",
     "SPEECH OUTPUT: 'Amusing numbers fall between'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'and'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: '.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  ' $l I'm a label'",
     "     VISIBLE:  ' $l I'm a label', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'I'm a label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  ' $l Am I a label as well?'",
     "     VISIBLE:  ' $l Am I a label as well?', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'Am I a label as well?.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'What the heck should we do here? h2'",
     "     VISIBLE:  'What the heck should we do here?', cursor=1",
     "SPEECH OUTPUT: 'What the heck should we do here? heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Looking at what follows visually, I'm not sure what I would type/i.e. what the labels are.'",
     "     VISIBLE:  'Looking at what follows visually', cursor=1",
     "SPEECH OUTPUT: 'Looking at what follows visually, I'm not sure what I would type/i.e. what the labels are.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  ' $l Too far away to be a label.'",
     "     VISIBLE:  ' $l Too far away to be a label.', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'Too far away to be a label.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Distance doesn't count on the left $l'",
     "     VISIBLE:  'Distance doesn't count on the le', cursor=1",
     "SPEECH OUTPUT: 'Distance doesn't count on the left.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Sometimes labels can be below the fields due to <br /> h2'",
     "     VISIBLE:  'Sometimes labels can be below th', cursor=1",
     "SPEECH OUTPUT: 'Sometimes labels can be below the fields due to <br /> heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'First Name'",
     "     VISIBLE:  'First Name', cursor=1",
     "SPEECH OUTPUT: 'First Name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'M.I.'",
     "     VISIBLE:  'M.I.', cursor=1",
     "SPEECH OUTPUT: 'M.I.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'Last Name'",
     "     VISIBLE:  'Last Name', cursor=1",
     "SPEECH OUTPUT: 'Last Name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'Other times it's due to layout tables h2'",
     "     VISIBLE:  'Other times it's due to layout t', cursor=1",
     "SPEECH OUTPUT: 'Other times it's due to layout tables heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'First name'",
     "     VISIBLE:  'First name', cursor=1",
     "SPEECH OUTPUT: 'First name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  'Middle'",
     "     VISIBLE:  'Middle', cursor=1",
     "SPEECH OUTPUT: 'Middle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'initial'",
     "     VISIBLE:  'initial', cursor=1",
     "SPEECH OUTPUT: 'initial.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  'Last name'",
     "     VISIBLE:  'Last name', cursor=1",
     "SPEECH OUTPUT: 'Last.'",
     "SPEECH OUTPUT: 'name'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  'Second verse same as the first (only now the labels are above the fields) h2'",
     "     VISIBLE:  'Second verse same as the first (', cursor=1",
     "SPEECH OUTPUT: 'Second verse same as the first (only now the labels are above the fields) heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Down",
    ["BRAILLE LINE:  'First Name'",
     "     VISIBLE:  'First Name', cursor=1",
     "SPEECH OUTPUT: 'First Name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Down",
    ["BRAILLE LINE:  'Middle'",
     "     VISIBLE:  'Middle', cursor=1",
     "SPEECH OUTPUT: 'Middle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Down",
    ["BRAILLE LINE:  'initial'",
     "     VISIBLE:  'initial', cursor=1",
     "SPEECH OUTPUT: 'initial.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Down",
    ["BRAILLE LINE:  'Last name'",
     "     VISIBLE:  'Last name', cursor=1",
     "SPEECH OUTPUT: 'Last.'",
     "SPEECH OUTPUT: 'name'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Down",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Down",
    ["BRAILLE LINE:  'Decisions, decisions.... When in doubt, closest table cell text wins h2'",
     "     VISIBLE:  'Decisions, decisions.... When in', cursor=1",
     "SPEECH OUTPUT: 'Decisions, decisions.... When in doubt, closest table cell text wins heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Down",
    ["BRAILLE LINE:  'First name Middle'",
     "     VISIBLE:  'First name Middle', cursor=1",
     "SPEECH OUTPUT: 'First name.'",
     "SPEECH OUTPUT: 'Middle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  'Decisions, decisions.... When in doubt, closest table cell text wins h2'",
     "     VISIBLE:  'Decisions, decisions.... When in', cursor=1",
     "SPEECH OUTPUT: 'Decisions, decisions.... When in doubt, closest table cell text wins heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Up",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Up",
    ["BRAILLE LINE:  'Last name'",
     "     VISIBLE:  'Last name', cursor=1",
     "SPEECH OUTPUT: 'Last.'",
     "SPEECH OUTPUT: 'name'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'initial'",
     "     VISIBLE:  'initial', cursor=1",
     "SPEECH OUTPUT: 'initial.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  'Middle'",
     "     VISIBLE:  'Middle', cursor=1",
     "SPEECH OUTPUT: 'Middle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'First Name'",
     "     VISIBLE:  'First Name', cursor=1",
     "SPEECH OUTPUT: 'First Name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  'Second verse same as the first (only now the labels are above the fields) h2'",
     "     VISIBLE:  'Second verse same as the first (', cursor=1",
     "SPEECH OUTPUT: 'Second verse same as the first (only now the labels are above the fields) heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  'Last name'",
     "     VISIBLE:  'Last name', cursor=1",
     "SPEECH OUTPUT: 'Last.'",
     "SPEECH OUTPUT: 'name'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  'initial'",
     "     VISIBLE:  'initial', cursor=1",
     "SPEECH OUTPUT: 'initial.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  'Middle'",
     "     VISIBLE:  'Middle', cursor=1",
     "SPEECH OUTPUT: 'Middle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  'First name'",
     "     VISIBLE:  'First name', cursor=1",
     "SPEECH OUTPUT: 'First name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'Other times it's due to layout tables h2'",
     "     VISIBLE:  'Other times it's due to layout t', cursor=1",
     "SPEECH OUTPUT: 'Other times it's due to layout tables heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  'Last Name'",
     "     VISIBLE:  'Last Name', cursor=1",
     "SPEECH OUTPUT: 'Last Name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Up",
    ["BRAILLE LINE:  'M.I.'",
     "     VISIBLE:  'M.I.', cursor=1",
     "SPEECH OUTPUT: 'M.I.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "48. Line Up",
    ["BRAILLE LINE:  'First Name'",
     "     VISIBLE:  'First Name', cursor=1",
     "SPEECH OUTPUT: 'First Name.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "49. Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "50. Line Up",
    ["BRAILLE LINE:  'Sometimes labels can be below the fields due to <br /> h2'",
     "     VISIBLE:  'Sometimes labels can be below th', cursor=1",
     "SPEECH OUTPUT: 'Sometimes labels can be below the fields due to <br /> heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "51. Line Up",
    ["BRAILLE LINE:  'Distance doesn't count on the left $l'",
     "     VISIBLE:  'Distance doesn't count on the le', cursor=1",
     "SPEECH OUTPUT: 'Distance doesn't count on the left.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "52. Line Up",
    ["BRAILLE LINE:  ' $l Too far away to be a label.'",
     "     VISIBLE:  ' $l Too far away to be a label.', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'Too far away to be a label.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "53. Line Up",
    ["BRAILLE LINE:  'Looking at what follows visually, I'm not sure what I would type/i.e. what the labels are.'",
     "     VISIBLE:  'Looking at what follows visually', cursor=1",
     "SPEECH OUTPUT: 'Looking at what follows visually, I'm not sure what I would type/i.e. what the labels are.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "54. Line Up",
    ["BRAILLE LINE:  'What the heck should we do here? h2'",
     "     VISIBLE:  'What the heck should we do here?', cursor=1",
     "SPEECH OUTPUT: 'What the heck should we do here? heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "55. Line Up",
    ["BRAILLE LINE:  ' $l Am I a label as well?'",
     "     VISIBLE:  ' $l Am I a label as well?', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'Am I a label as well?.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "56. Line Up",
    ["BRAILLE LINE:  ' $l I'm a label'",
     "     VISIBLE:  ' $l I'm a label', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'I'm a label'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "57. Line Up",
    ["BRAILLE LINE:  'Amusing numbers fall between  $l and  $l.'",
     "     VISIBLE:  'Amusing numbers fall between  $l', cursor=1",
     "SPEECH OUTPUT: 'Amusing numbers fall between'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'and'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: '.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "58. Line Up",
    ["BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  'Type something rather amusing he', cursor=1",
     "SPEECH OUTPUT: 'Type'",
     "SPEECH OUTPUT: 'something'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'rather'",
     "SPEECH OUTPUT: 'amusing'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'here:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "59. Line Up",
    ["BRAILLE LINE:  'Here are some entries h2'",
     "     VISIBLE:  'Here are some entries h2', cursor=1",
     "SPEECH OUTPUT: 'Here are some entries heading level 2'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
