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

sequence.append(PauseAction(3000))
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("a"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
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
    "2. Line Down",
    ["BRAILLE LINE:  'Short Bug Search Form Complicated Bug Search Form'",
     "     VISIBLE:  'Short Bug Search Form Complicate', cursor=1",
     "SPEECH OUTPUT: 'Short Bug Search Form'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Complicated Bug Search Form.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Give me some help (reloads page.)'",
     "     VISIBLE:  'Give me some help (reloads page.', cursor=1",
     "SPEECH OUTPUT: 'Give me some help'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(reloads page.)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Summary: contains all of the words/strings combo box $l Search push button'",
     "     VISIBLE:  'Summary: contains all of the wor', cursor=1",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'table with 5 rows 4 columns'",
     "SPEECH OUTPUT: 'Summary:'",
     "SPEECH OUTPUT: 'contains all of the words/strings combo box.'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'Search push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Classification:'",
     "     VISIBLE:  'Classification:', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Classification: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 8 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Product:'",
     "     VISIBLE:  'Product:', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Product: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 379 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ': column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 1248 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'Version:'",
     "     VISIBLE:  'Version:', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Version: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 857 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'Target Milestone:'",
     "     VISIBLE:  'Target Milestone:', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Target Milestone: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 555 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'A Comment: contains the string combo box $l'",
     "     VISIBLE:  'A Comment: contains the string c', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'A Comment:'",
     "SPEECH OUTPUT: 'contains the string combo box.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'Whiteboard: contains all of the words/strings combo box $l'",
     "     VISIBLE:  'Whiteboard: contains all of the ', cursor=1",
     "SPEECH OUTPUT: 'Whiteboard:'",
     "SPEECH OUTPUT: 'contains all of the words/strings combo box.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'Keywords: contains all of the keywords combo box $l'",
     "     VISIBLE:  'Keywords: contains all of the ke', cursor=1",
     "SPEECH OUTPUT: 'Keywords'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'contains all of the keywords combo box.'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'Status:'",
     "     VISIBLE:  'Status:', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Status: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["KNOWN ISSUE: Should we be doing a different presentation of these selected children?",
     "BRAILLE LINE:  'UNCONFIRMED NEW ASSIGNED REOPENED NEEDINFO list box'",
     "     VISIBLE:  'UNCONFIRMED NEW ASSIGNED REOPENE', cursor=1",
     "SPEECH OUTPUT: 'UNCONFIRMED NEW ASSIGNED REOPENED NEEDINFO.'",
     "SPEECH OUTPUT: 'multi-select List with 8 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'Resolution:'",
     "     VISIBLE:  'Resolution:', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Resolution: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 12 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  'Severity:'",
     "     VISIBLE:  'Severity:', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Severity: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 7 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Down",
    ["BRAILLE LINE:  'Priority:'",
     "     VISIBLE:  'Priority:', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Priority: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 5 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Down",
    ["BRAILLE LINE:  'OS:'",
     "     VISIBLE:  'OS:', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'OS: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 21 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Down",
    ["BRAILLE LINE:  'Email and Numbering'",
     "     VISIBLE:  'Email and Numbering', cursor=1",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'Email and Numbering panel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Down",
    ["BRAILLE LINE:  'Any one of:'",
     "     VISIBLE:  'Any one of:', cursor=1",
     "SPEECH OUTPUT: 'Any one of:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Down",
    ["BRAILLE LINE:  '<x> the bug assignee check box'",
     "     VISIBLE:  '<x> the bug assignee check box', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Down",
    ["BRAILLE LINE:  '< > the reporter check box'",
     "     VISIBLE:  '< > the reporter check box', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Down",
    ["BRAILLE LINE:  '< > the QA contact check box'",
     "     VISIBLE:  '< > the QA contact check box', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Down",
    ["BRAILLE LINE:  '< > a CC list member check box'",
     "     VISIBLE:  '< > a CC list member check box', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Down",
    ["BRAILLE LINE:  '< > a commenter check box'",
     "     VISIBLE:  '< > a commenter check box', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Down",
    ["BRAILLE LINE:  'contains combo box'",
     "     VISIBLE:  'contains combo box', cursor=1",
     "SPEECH OUTPUT: 'contains combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Down",
    ["BRAILLE LINE:  'Any one of:'",
     "     VISIBLE:  'Any one of:', cursor=1",
     "SPEECH OUTPUT: 'Any one of:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Down",
    ["BRAILLE LINE:  '<x> the bug assignee check box'",
     "     VISIBLE:  '<x> the bug assignee check box', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Down",
    ["BRAILLE LINE:  '<x> the reporter check box'",
     "     VISIBLE:  '<x> the reporter check box', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Down",
    ["BRAILLE LINE:  '<x> the QA contact check box'",
     "     VISIBLE:  '<x> the QA contact check box', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Down",
    ["BRAILLE LINE:  '<x> a CC list member check box'",
     "     VISIBLE:  '<x> a CC list member check box', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Down",
    ["BRAILLE LINE:  '< > a commenter check box'",
     "     VISIBLE:  '< > a commenter check box', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Down",
    ["BRAILLE LINE:  'contains combo box'",
     "     VISIBLE:  'contains combo box', cursor=1",
     "SPEECH OUTPUT: 'contains combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Down",
    ["BRAILLE LINE:  'Only include combo box bugs numbered:  $l'",
     "     VISIBLE:  'Only include combo box bugs numb', cursor=1",
     "SPEECH OUTPUT: 'Only include combo box.'",
     "SPEECH OUTPUT: 'bugs numbered:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "48. Line Down",
    ["BRAILLE LINE:  '(comma-separated list)'",
     "     VISIBLE:  '(comma-separated list)', cursor=1",
     "SPEECH OUTPUT: '(comma-separated list)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "49. Line Down",
    ["BRAILLE LINE:  'Bug Changes'",
     "     VISIBLE:  'Bug Changes', cursor=1",
     "SPEECH OUTPUT: 'Bug Changes panel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "50. Line Down",
    ["BRAILLE LINE:  'Only bugs changed between:'",
     "     VISIBLE:  'Only bugs changed between:', cursor=1",
     "SPEECH OUTPUT: 'Only bugs changed between:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "51. Line Down",
    ["BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'and'",
     "SPEECH OUTPUT: 'entry Now.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "52. Line Down",
    ["BRAILLE LINE:  '(YYYY-MM-DD or relative dates)'",
     "     VISIBLE:  '(YYYY-MM-DD or relative dates)', cursor=1",
     "SPEECH OUTPUT: '(YYYY-MM-DD or relative dates)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "53. Line Down",
    ["BRAILLE LINE:  'where one or more of the following changed:'",
     "     VISIBLE:  'where one or more of the followi', cursor=1",
     "SPEECH OUTPUT: 'where one or more of the following changed:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "54. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 26 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "55. Line Down",
    ["BRAILLE LINE:  'and the new value was:'",
     "     VISIBLE:  'and the new value was:', cursor=1",
     "SPEECH OUTPUT: 'and the new value was:.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "56. Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=0",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "57. Line Down",
    ["BRAILLE LINE:  'GNOME version:'",
     "     VISIBLE:  'GNOME version:', cursor=1",
     "SPEECH OUTPUT: 'GNOME version: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "58. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 14 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "59. Line Down",
    ["BRAILLE LINE:  'GNOME target:'",
     "     VISIBLE:  'GNOME target:', cursor=1",
     "SPEECH OUTPUT: 'GNOME target: column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "60. Line Down",
    ["BRAILLE LINE:  'list box'",
     "     VISIBLE:  'list box', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 12 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "61. Line Down",
    ["BRAILLE LINE:  'Sort results by: Reuse same sort as last time combo box'",
     "     VISIBLE:  'Sort results by: Reuse same sort', cursor=1",
     "SPEECH OUTPUT: 'Sort results by:'",
     "SPEECH OUTPUT: 'Reuse same sort as last time combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "62. Line Down",
    ["BRAILLE LINE:  'Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "SPEECH OUTPUT: 'Search push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "63. Line Down",
    ["BRAILLE LINE:  '< > and remember these as my default search options check box'",
     "     VISIBLE:  '< > and remember these as my def', cursor=0",
     "SPEECH OUTPUT: 'and remember these as my default search options check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "64. Line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "65. Line Down",
    ["BRAILLE LINE:  'Advanced Searching Using Boolean Charts:'",
     "     VISIBLE:  'Advanced Searching Using Boolean', cursor=1",
     "SPEECH OUTPUT: 'Advanced Searching Using Boolean Charts:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "66. Line Down",
    ["BRAILLE LINE:  '< > Not (negate this whole chart) check box'",
     "     VISIBLE:  '< > Not \\(negate this whole chart', cursor=1",
     "SPEECH OUTPUT: 'Not (negate this whole chart) check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "67. Line Down",
    ["BRAILLE LINE:  '--- combo box --- combo box $l Or push button'",
     "     VISIBLE:  '--- combo box --- combo box $l O', cursor=1",
     "SPEECH OUTPUT: '--- combo box.'",
     "SPEECH OUTPUT: '--- combo box.'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'Or push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "68. Line Down",
    ["BRAILLE LINE:  'And push button Add another boolean chart push button'",
     "     VISIBLE:  'And push button Add another bool', cursor=1",
     "SPEECH OUTPUT: 'And push button'",
     "SPEECH OUTPUT: 'Add another boolean chart push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "69. Line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "70. Line Down",
    ["BRAILLE LINE:  'Saved Searches: My Bugs and Patches | All Orca | Firefox | open orca | Open RFEs'",
     "     VISIBLE:  'Saved Searches: My Bugs and Patc', cursor=1",
     "SPEECH OUTPUT: 'Saved Searches:'",
     "SPEECH OUTPUT: 'My Bugs and Patches'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '|'",
     "SPEECH OUTPUT: 'All Orca'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '|'",
     "SPEECH OUTPUT: 'Firefox'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '|'",
     "SPEECH OUTPUT: 'open orca'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '|'",
     "SPEECH OUTPUT: 'Open RFEs'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
