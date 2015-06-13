#!/usr/bin/python

"""Test of line navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Home Bugzilla'",
     "     VISIBLE:  'Home Bugzilla', cursor=1",
     "SPEECH OUTPUT: 'Home link'",
     "SPEECH OUTPUT: 'Bugzilla'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'New bug · Browse · Search · Repo', cursor=1",
     "SPEECH OUTPUT: 'New bug link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Browse link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Search link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Reports link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Account link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Admin link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Help link'",
     "SPEECH OUTPUT: 'Logged In joanmarie.diggs@gmail.com |'",
     "SPEECH OUTPUT: 'Log Out link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Enter Bug: orca – This page lets you enter a new bug  h1'",
     "     VISIBLE:  'Enter Bug: orca – This page lets', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca – This page lets you enter a new bug heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'into Bugzilla. h1'",
     "     VISIBLE:  'into Bugzilla. h1', cursor=1",
     "SPEECH OUTPUT: 'into Bugzilla. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Before reporting a bug, please read the bug writing guidelines,'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the'",
     "SPEECH OUTPUT: 'bug writing guidelines link'",
     "SPEECH OUTPUT: ','"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'please look at the list of most frequently reported bugs, and please'",
     "     VISIBLE:  'please look at the list of most ', cursor=1",
     "SPEECH OUTPUT: 'please look at the list of'",
     "SPEECH OUTPUT: 'most frequently reported bugs link'",
     "SPEECH OUTPUT: ', and please'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'search or browse for the bug.'",
     "     VISIBLE:  'search or browse for the bug.', cursor=1",
     "SPEECH OUTPUT: 'search link'",
     "SPEECH OUTPUT: 'or'",
     "SPEECH OUTPUT: 'browse link'",
     "SPEECH OUTPUT: 'for the bug.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'Reporter: joanmarie.diggs@gmail.com Product: orca'",
     "     VISIBLE:  'Reporter: joanmarie.diggs@gmail.', cursor=1",
     "SPEECH OUTPUT: 'Reporter:'",
     "SPEECH OUTPUT: 'joanmarie.diggs@gmail.com'",
     "SPEECH OUTPUT: 'Product:'",
     "SPEECH OUTPUT: 'orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Version:'",
     "     VISIBLE:  'Version:', cursor=1",
     "SPEECH OUTPUT: 'Version:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  '2.21.x  list box'",
     "     VISIBLE:  '2.21.x  list box', cursor=1",
     "SPEECH OUTPUT: '2.21.x  List with 9 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component link'",
     "SPEECH OUTPUT: ':'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'braille  list box'",
     "     VISIBLE:  'braille  list box', cursor=1",
     "SPEECH OUTPUT: 'braille  List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'GNOME'",
     "     VISIBLE:  'GNOME', cursor=1",
     "SPEECH OUTPUT: 'GNOME'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'version:'",
     "     VISIBLE:  'version:', cursor=1",
     "SPEECH OUTPUT: 'version'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ':'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'Unspecified combo box'",
     "     VISIBLE:  'Unspecified combo box', cursor=1",
     "SPEECH OUTPUT: 'Unspecified combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'OS: Linux combo box'",
     "     VISIBLE:  'OS: Linux combo box', cursor=1",
     "SPEECH OUTPUT: 'OS link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'Linux combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'Severity: normal combo box'",
     "     VISIBLE:  'Severity: normal combo box', cursor=1",
     "SPEECH OUTPUT: 'Severity link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'normal combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'Summary: $l'",
     "     VISIBLE:  'Summary: $l', cursor=1",
     "SPEECH OUTPUT: 'Summary:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'Description:'",
     "     VISIBLE:  'Description:', cursor=1",
     "SPEECH OUTPUT: 'Description:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'Optional Fields'",
     "     VISIBLE:  'Optional Fields', cursor=1",
     "SPEECH OUTPUT: 'Optional Fields'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  'Cc: $l'",
     "     VISIBLE:  'Cc: $l', cursor=1",
     "SPEECH OUTPUT: 'Cc:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  'Keywords:  $l'",
     "     VISIBLE:  'Keywords:  $l', cursor=1",
     "SPEECH OUTPUT: 'Keywords link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Down",
    ["BRAILLE LINE:  'Depends'",
     "     VISIBLE:  'Depends', cursor=1",
     "SPEECH OUTPUT: 'Depends'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  'Keywords:  $l'",
     "     VISIBLE:  'Keywords:  $l', cursor=1",
     "SPEECH OUTPUT: 'Keywords link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Up",
    ["BRAILLE LINE:  'Cc: $l'",
     "     VISIBLE:  'Cc: $l', cursor=1",
     "SPEECH OUTPUT: 'Cc:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Up",
    ["BRAILLE LINE:  'Optional Fields'",
     "     VISIBLE:  'Optional Fields', cursor=1",
     "SPEECH OUTPUT: 'Optional Fields'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'Description:'",
     "     VISIBLE:  'Description:', cursor=1",
     "SPEECH OUTPUT: 'Description:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Up",
    ["BRAILLE LINE:  'Summary: $l'",
     "     VISIBLE:  'Summary: $l', cursor=1",
     "SPEECH OUTPUT: 'Summary:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  'Severity: normal combo box'",
     "     VISIBLE:  'Severity: normal combo box', cursor=1",
     "SPEECH OUTPUT: 'Severity link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'normal combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Up",
    ["BRAILLE LINE:  'OS: Linux combo box'",
     "     VISIBLE:  'OS: Linux combo box', cursor=1",
     "SPEECH OUTPUT: 'OS link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'Linux combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Up",
    ["BRAILLE LINE:  'Unspecified combo box'",
     "     VISIBLE:  'Unspecified combo box', cursor=1",
     "SPEECH OUTPUT: 'Unspecified combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'version:'",
     "     VISIBLE:  'version:', cursor=1",
     "SPEECH OUTPUT: 'version",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ':'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  'GNOME'",
     "     VISIBLE:  'GNOME', cursor=1",
     "SPEECH OUTPUT: 'GNOME'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'braille  list box'",
     "     VISIBLE:  'braille  list box', cursor=1",
     "SPEECH OUTPUT: 'braille  List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component link'",
     "SPEECH OUTPUT: ':'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  '2.21.x  list box'",
     "     VISIBLE:  '2.21.x  list box', cursor=1",
     "SPEECH OUTPUT: '2.21.x  List with 9 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  'Version:'",
     "     VISIBLE:  'Version:', cursor=1",
     "SPEECH OUTPUT: 'Version:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  'Reporter: joanmarie.diggs@gmail.com Product: orca'",
     "     VISIBLE:  'Reporter: joanmarie.diggs@gmail.', cursor=1",
     "SPEECH OUTPUT: 'Reporter:'",
     "SPEECH OUTPUT: 'joanmarie.diggs@gmail.com'",
     "SPEECH OUTPUT: 'Product:'",
     "SPEECH OUTPUT: 'orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  'search or browse for the bug.'",
     "     VISIBLE:  'search or browse for the bug.', cursor=1",
     "SPEECH OUTPUT: 'search link'",
     "SPEECH OUTPUT: 'or'",
     "SPEECH OUTPUT: 'browse link'",
     "SPEECH OUTPUT: 'for the bug.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  'please look at the list of most frequently reported bugs, and please'",
     "     VISIBLE:  'please look at the list of most ', cursor=1",
     "SPEECH OUTPUT: 'please look at the list of'",
     "SPEECH OUTPUT: 'most frequently reported bugs link'",
     "SPEECH OUTPUT: ', and please'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'Before reporting a bug, please read the bug writing guidelines,'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the'",
     "SPEECH OUTPUT: 'bug writing guidelines link'",
     "SPEECH OUTPUT: ','"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  'into Bugzilla. h1'",
     "     VISIBLE:  'into Bugzilla. h1', cursor=1",
     "SPEECH OUTPUT: 'into Bugzilla. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  'Enter Bug: orca \u2013 This page lets you enter a new bug  h1'",
     "     VISIBLE:  'Enter Bug: orca – This page lets', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca \u2013 This page lets you enter a new bug heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Up",
    ["BRAILLE LINE:  'New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'New bug · Browse · Search · Repo', cursor=1",
     "SPEECH OUTPUT: 'New bug link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Browse link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Search link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Reports link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Account link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Admin link'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Help link'",
     "SPEECH OUTPUT: 'Logged In joanmarie.diggs@gmail.com |'",
     "SPEECH OUTPUT: 'Log Out link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Up",
    ["BRAILLE LINE:  'Home Bugzilla'",
     "     VISIBLE:  'Home Bugzilla', cursor=1",
     "SPEECH OUTPUT: 'Home link'",
     "SPEECH OUTPUT: 'Bugzilla'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
