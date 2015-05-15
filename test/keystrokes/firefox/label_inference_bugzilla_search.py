#!/usr/bin/python

"""Test of label guess for bugzilla's advanced search page."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift Tab",
    ["BRAILLE LINE:  'contains all of the words/strings combo box'",
     "     VISIBLE:  'contains all of the words/string', cursor=1",
     "SPEECH OUTPUT: 'Summary: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Search push button'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  'Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "BRAILLE LINE:  'Admin'",
     "     VISIBLE:  'Admin', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Classification: multi-select List with 8 items'",
     "SPEECH OUTPUT: 'Admin '",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab",
    ["BRAILLE LINE:  'Admin'",
     "     VISIBLE:  'Admin', cursor=1",
     "BRAILLE LINE:  'accerciser'",
     "     VISIBLE:  'accerciser', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Product: multi-select List with 379 items'",
     "SPEECH OUTPUT: 'accerciser'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab",
    ["BRAILLE LINE:  'Component'",
     "     VISIBLE:  'Component', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component link'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab",
    ["BRAILLE LINE:  'abiscan'",
     "     VISIBLE:  'abiscan', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Component: multi-select List with 1248 items'",
     "SPEECH OUTPUT: 'abiscan'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Tab",
    ["BRAILLE LINE:  'abiscan'",
     "     VISIBLE:  'abiscan', cursor=1",
     "BRAILLE LINE:  '0.0.1'",
     "     VISIBLE:  '0.0.1', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Version: multi-select List with 857 items'",
     "SPEECH OUTPUT: '0.0.1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab",
    ["BRAILLE LINE:  '---'",
     "     VISIBLE:  '---', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Target Milestone: multi-select List with 555 items'",
     "SPEECH OUTPUT: '---'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "10. Tab",
    ["BRAILLE LINE:  'contains the string combo box'",
     "     VISIBLE:  'contains the string combo box', cursor=1",
     "SPEECH OUTPUT: 'A Comment: contains the string combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "11. Tab",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "12. Tab",
    ["BRAILLE LINE:  'contains all of the words/strings combo box'",
     "     VISIBLE:  'contains all of the words/string', cursor=1",
     "SPEECH OUTPUT: 'Whiteboard: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "13. Tab",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "14. Tab",
    ["BRAILLE LINE:  'Keywords'",
     "     VISIBLE:  'Keywords', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "BRAILLE LINE:  'Keywords: contains all of the keywords combo box $l'",
     "     VISIBLE:  'Keywords: contains all of the ke', cursor=1",
     "SPEECH OUTPUT: 'Keywords link'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "15. Tab",
    ["BRAILLE LINE:  'Keywords: contains all of the keywords combo box $l'",
     "     VISIBLE:  'contains all of the keywords com', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Keywords: contains all of the keywords combo box'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "16. Tab",
    ["BRAILLE LINE:  'Keywords: contains all of the keywords combo box $l'",
     "     VISIBLE:  'contains all of the keywords com', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "17. Tab",
    ["BRAILLE LINE:  'UNCONFIRMED'",
     "     VISIBLE:  'UNCONFIRMED', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Status: multi-select List with 8 items'",
     "SPEECH OUTPUT: 'UNCONFIRMED'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "18. Tab",
    ["BRAILLE LINE:  'FIXED'",
     "     VISIBLE:  'FIXED', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Resolution: multi-select List with 12 items'",
     "SPEECH OUTPUT: 'FIXED'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "19. Tab",
    ["BRAILLE LINE:  'blocker'",
     "     VISIBLE:  'blocker', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Severity: multi-select List with 7 items'",
     "SPEECH OUTPUT: 'blocker'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "20. Tab",
    ["BRAILLE LINE:  'Immediate'",
     "     VISIBLE:  'Immediate', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'Priority: multi-select List with 5 items'",
     "SPEECH OUTPUT: 'Immediate'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "21. Tab",
    ["BRAILLE LINE:  'All'",
     "     VISIBLE:  'All', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'OS: multi-select List with 21 items'",
     "SPEECH OUTPUT: 'All'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "22. Tab",
    ["BRAILLE LINE:  '<x> check box'",
     "     VISIBLE:  '<x> check box', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Email and Numbering  panel'",
     "SPEECH OUTPUT: 'the bug assignee check box checked'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "23. Tab",
    ["BRAILLE LINE:  '<x> check box'",
     "     VISIBLE:  '<x> check box', cursor=1",
     "BRAILLE LINE:  '< > check box the reporter'",
     "     VISIBLE:  '< > check box the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "24. Tab",
    ["BRAILLE LINE:  '< > check box the QA contact'",
     "     VISIBLE:  '< > check box the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "25. Tab",
    ["BRAILLE LINE:  '< > check box a CC list member'",
     "     VISIBLE:  '< > check box a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "26. Tab",
    ["BRAILLE LINE:  '< > check box a commenter'",
     "     VISIBLE:  '< > check box a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "27. Tab",
    ["BRAILLE LINE:  'contains combo box'",
     "     VISIBLE:  'contains combo box', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'contains combo box'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "28. Tab",
    ["BRAILLE LINE:  'contains combo box'",
     "     VISIBLE:  'contains combo box', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "29. Tab",
    ["BRAILLE LINE:  '<x> check box'",
     "     VISIBLE:  '<x> check box', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'the bug assignee check box checked'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "30. Tab",
    ["BRAILLE LINE:  '<x> check box'",
     "     VISIBLE:  '<x> check box', cursor=1",
     "BRAILLE LINE:  '<x> check box the reporter'",
     "     VISIBLE:  '<x> check box the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "31. Tab",
    ["BRAILLE LINE:  '<x> check box the QA contact'",
     "     VISIBLE:  '<x> check box the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "32. Tab",
    ["BRAILLE LINE:  '<x> check box a CC list member'",
     "     VISIBLE:  '<x> check box a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "33. Tab",
    ["BRAILLE LINE:  '< > check box a commenter'",
     "     VISIBLE:  '< > check box a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "34. Tab",
    ["BRAILLE LINE:  'contains combo box'",
     "     VISIBLE:  'contains combo box', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'contains combo box'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "35. Tab",
    ["BRAILLE LINE:  'contains combo box'",
     "     VISIBLE:  'contains combo box', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "36. Tab",
    ["BRAILLE LINE:  'Only include combo box'",
     "     VISIBLE:  'Only include combo box', cursor=1",
     "SPEECH OUTPUT: 'Only include combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "37. Tab",
    ["KNOWN ISSUE: This could be improved",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: '(comma-separated list) entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "38. Tab",
    ["KNOWN ISSUE: This could be improved",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Bug Changes panel'",
     "SPEECH OUTPUT: '(YYYY-MM-DD or relative dates) entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "39. Tab",
    ["BRAILLE LINE:  'Now $l'",
     "     VISIBLE:  'Now $l', cursor=4",
     "BRAILLE LINE:  'Now $l'",
     "     VISIBLE:  'Now $l', cursor=4",
     "SPEECH OUTPUT: 'and entry Now selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "40. Tab",
    ["BRAILLE LINE:  '[Bug creation]'",
     "     VISIBLE:  '[Bug creation]', cursor=1",
     "SPEECH OUTPUT: 'multi-select List with 26 items'",
     "SPEECH OUTPUT: '[Bug creation]'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "41. Tab",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "42. Tab",
    ["BRAILLE LINE:  'Unspecified'",
     "     VISIBLE:  'Unspecified', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'GNOME version: multi-select List with 14 items'",
     "SPEECH OUTPUT: 'Unspecified'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "43. Tab",
    ["BRAILLE LINE:  'Unspecified'",
     "     VISIBLE:  'Unspecified', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 1 column'",
     "SPEECH OUTPUT: 'GNOME target: multi-select List with 12 items'",
     "SPEECH OUTPUT: 'Unspecified'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "44. Tab",
    ["BRAILLE LINE:  'Reuse same sort as last time combo box'",
     "     VISIBLE:  'Reuse same sort as last time com', cursor=1",
     "SPEECH OUTPUT: 'Sort results by: Reuse same sort as last time combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "45. Tab",
    ["BRAILLE LINE:  'Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Search push button'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "46. Tab",
    ["BRAILLE LINE:  'Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "BRAILLE LINE:  '< > check box and remember these as my default search options'",
     "     VISIBLE:  '< > check box and remember these', cursor=1",
     "SPEECH OUTPUT: 'and remember these as my default search options check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "47. Tab",
    ["BRAILLE LINE:  '< > check box Not (negate this whole chart)'",
     "     VISIBLE:  '< > check box Not \(negate this w', cursor=1",
     "SPEECH OUTPUT: 'Not (negate this whole chart) check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "48. Tab",
    ["BRAILLE LINE:  '--- combo box --- combo box $l Or push button'",
     "     VISIBLE:  '--- combo box --- combo box $l O', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: '--- combo box'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "49. Tab",
    ["BRAILLE LINE:  '--- combo box --- combo box $l Or push button'",
     "     VISIBLE:  '--- combo box --- combo box $l O', cursor=1",
     "BRAILLE LINE:  '--- combo box'",
     "     VISIBLE:  '--- combo box', cursor=1",
     "SPEECH OUTPUT: '--- combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "50. Tab",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
