#!/usr/bin/python

"""Test of line navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Home Bugzilla'",
     "     VISIBLE:  'Home Bugzilla', cursor=1",
     "SPEECH OUTPUT: 'Home link.'",
     "SPEECH OUTPUT: 'Bugzilla'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'New bug · Browse · Search · Repo', cursor=1",
     "SPEECH OUTPUT: 'New bug'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Browse'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Search'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Reports'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Account'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Admin'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Help'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Logged In joanmarie.diggs@gmail.com |'",
     "SPEECH OUTPUT: 'Log Out'",
     "SPEECH OUTPUT: 'link.'"]))

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
    ["BRAILLE LINE:  'Before reporting a bug, please read the bug writing guidelines, please look at the list of most'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the.'",
     "SPEECH OUTPUT: 'bug writing guidelines'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ', please look at the list of.'",
     "SPEECH OUTPUT: 'most'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'frequently reported bugs, and please search or browse for the bug.'",
     "     VISIBLE:  'frequently reported bugs, and pl', cursor=1",
     "SPEECH OUTPUT: 'frequently reported bugs'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ', and please.'",
     "SPEECH OUTPUT: 'search'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'or.'",
     "SPEECH OUTPUT: 'browse'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'for the bug.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Reporter: joanmarie.diggs@gmail.com Product: orca'",
     "     VISIBLE:  'Reporter: joanmarie.diggs@gmail.', cursor=1",
     "SPEECH OUTPUT: 'Reporter:.'",
     "SPEECH OUTPUT: 'joanmarie.diggs@gmail.com.'",
     "SPEECH OUTPUT: 'Product:.'",
     "SPEECH OUTPUT: 'orca.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'Version:'",
     "     VISIBLE:  'Version:', cursor=1",
     "SPEECH OUTPUT: 'Version:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  '2.21.x  list box'",
     "     VISIBLE:  '2.21.x  list box', cursor=1",
     "SPEECH OUTPUT: '2.21.x.'",
     "SPEECH OUTPUT: 'List with 9 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'List with 5 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'GNOME'",
     "     VISIBLE:  'GNOME', cursor=1",
     "SPEECH OUTPUT: 'GNOME'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'version:'",
     "     VISIBLE:  'version:', cursor=1",
     "SPEECH OUTPUT: 'version'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Unspecified combo box'",
     "     VISIBLE:  'Unspecified combo box', cursor=1",
     "SPEECH OUTPUT: 'Unspecified combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'OS: Linux combo box'",
     "     VISIBLE:  'OS: Linux combo box', cursor=1",
     "SPEECH OUTPUT: 'OS'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'",
     "SPEECH OUTPUT: 'Linux combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'Severity: normal combo box'",
     "     VISIBLE:  'Severity: normal combo box', cursor=1",
     "SPEECH OUTPUT: 'Severity'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'",
     "SPEECH OUTPUT: 'normal combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'Summary: $l'",
     "     VISIBLE:  'Summary: $l', cursor=1",
     "SPEECH OUTPUT: 'Summary:.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'Description:'",
     "     VISIBLE:  'Description:', cursor=1",
     "SPEECH OUTPUT: 'Description:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  'Optional Fields'",
     "     VISIBLE:  'Optional Fields', cursor=1",
     "SPEECH OUTPUT: 'Optional Fields.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'Cc: $l'",
     "     VISIBLE:  'Cc: $l', cursor=1",
     "SPEECH OUTPUT: 'Cc:.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  'Keywords:'",
     "     VISIBLE:  'Keywords:', cursor=1",
     "SPEECH OUTPUT: 'Keywords'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Up",
    ["BRAILLE LINE:  'Keywords:'",
     "     VISIBLE:  'Keywords:', cursor=1",
     "SPEECH OUTPUT: 'Keywords'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  'Cc: $l'",
     "     VISIBLE:  'Cc: $l', cursor=1",
     "SPEECH OUTPUT: 'Cc:.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Up",
    ["BRAILLE LINE:  'Optional Fields'",
     "     VISIBLE:  'Optional Fields', cursor=1",
     "SPEECH OUTPUT: 'Optional Fields.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Up",
    ["BRAILLE LINE:  'Description:'",
     "     VISIBLE:  'Description:', cursor=1",
     "SPEECH OUTPUT: 'Description:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'Summary: $l'",
     "     VISIBLE:  'Summary: $l', cursor=1",
     "SPEECH OUTPUT: 'Summary:.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Up",
    ["BRAILLE LINE:  'Severity: normal combo box'",
     "     VISIBLE:  'Severity: normal combo box', cursor=1",
     "SPEECH OUTPUT: 'Severity'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'",
     "SPEECH OUTPUT: 'normal combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  'OS: Linux combo box'",
     "     VISIBLE:  'OS: Linux combo box', cursor=1",
     "SPEECH OUTPUT: 'OS'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'",
     "SPEECH OUTPUT: 'Linux combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Up",
    ["BRAILLE LINE:  'Unspecified combo box'",
     "     VISIBLE:  'Unspecified combo box', cursor=1",
     "SPEECH OUTPUT: 'Unspecified combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Up",
    ["BRAILLE LINE:  'version:'",
     "     VISIBLE:  'version:', cursor=1",
     "SPEECH OUTPUT: 'version'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'GNOME'",
     "     VISIBLE:  'GNOME', cursor=1",
     "SPEECH OUTPUT: 'GNOME'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'List with 5 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  '2.21.x  list box'",
     "     VISIBLE:  '2.21.x  list box', cursor=1",
     "SPEECH OUTPUT: '2.21.x.'",
     "SPEECH OUTPUT: 'List with 9 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  'Version:'",
     "     VISIBLE:  'Version:', cursor=1",
     "SPEECH OUTPUT: 'Version:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  'Reporter: joanmarie.diggs@gmail.com Product: orca'",
     "     VISIBLE:  'Reporter: joanmarie.diggs@gmail.', cursor=1",
     "SPEECH OUTPUT: 'Reporter:.'",
     "SPEECH OUTPUT: 'joanmarie.diggs@gmail.com.'",
     "SPEECH OUTPUT: 'Product:.'",
     "SPEECH OUTPUT: 'orca.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  'frequently reported bugs, and please search or browse for the bug.'",
     "     VISIBLE:  'frequently reported bugs, and pl', cursor=1",
     "SPEECH OUTPUT: 'frequently reported bugs'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ', and please.'",
     "SPEECH OUTPUT: 'search'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'or.'",
     "SPEECH OUTPUT: 'browse'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'for the bug.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  'Before reporting a bug, please read the bug writing guidelines, please look at the list of most'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the.'",
     "SPEECH OUTPUT: 'bug writing guidelines'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ', please look at the list of.'",
     "SPEECH OUTPUT: 'most'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  'into Bugzilla. h1'",
     "     VISIBLE:  'into Bugzilla. h1', cursor=1",
     "SPEECH OUTPUT: 'into Bugzilla. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'Enter Bug: orca \u2013 This page lets you enter a new bug  h1'",
     "     VISIBLE:  'Enter Bug: orca – This page lets', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca \u2013 This page lets you enter a new bug heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  'New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'New bug · Browse · Search · Repo', cursor=1",
     "SPEECH OUTPUT: 'New bug'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Browse'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Search'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Reports'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Account'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Admin'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '·'",
     "SPEECH OUTPUT: 'Help'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Logged In joanmarie.diggs@gmail.com |'",
     "SPEECH OUTPUT: 'Log Out'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  'Home Bugzilla'",
     "     VISIBLE:  'Home Bugzilla', cursor=1",
     "SPEECH OUTPUT: 'Home link.'",
     "SPEECH OUTPUT: 'Bugzilla'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
