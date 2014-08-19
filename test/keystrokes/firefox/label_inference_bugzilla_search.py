#!/usr/bin/python

"""Test of label guess for bugzilla's advanced search page."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("a"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Toggle modes",
    ["BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "2. Top of File",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Home Bugzilla'",
     "     VISIBLE:  'Home Bugzilla', cursor=1",
     "BRAILLE LINE:  'Home Bugzilla'",
     "     VISIBLE:  'Home Bugzilla', cursor=0",
     "SPEECH OUTPUT: 'Home'",
     "SPEECH OUTPUT: 'Bugzilla'",
     "SPEECH OUTPUT: 'Home'",
     "SPEECH OUTPUT: 'link' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Next form field",
    ["KNOWN ISSUE: We are not displaying the current combo box item",
     "BRAILLE LINE:  'Summary: combo box $l Search push button'",
     "     VISIBLE:  ' combo box $l Search push button', cursor=1",
     "BRAILLE LINE:  'Summary: combo box $l Search push button'",
     "     VISIBLE:  ' combo box $l Search push button', cursor=1",
     "SPEECH OUTPUT: 'Summary: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Next form field",
    ["BRAILLE LINE:  'Summary: combo box $l Search push button'",
     "     VISIBLE:  ' $l Search push button', cursor=1",
     "BRAILLE LINE:  'Summary: combo box $l Search push button'",
     "     VISIBLE:  ' $l Search push button', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Next form field",
    ["BRAILLE LINE:  'Summary: combo box $l Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "BRAILLE LINE:  'Summary: combo box $l Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "SPEECH OUTPUT: 'Search push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Next form field",
    ["BRAILLE LINE:  'Admin'",
     "     VISIBLE:  'Admin', cursor=1",
     "BRAILLE LINE:  'Admin'",
     "     VISIBLE:  'Admin', cursor=1",
     "SPEECH OUTPUT: 'Classification: multi-select List with 8 items'",
     "SPEECH OUTPUT: 'Admin'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Next form field",
    ["BRAILLE LINE:  'accerciser'",
     "     VISIBLE:  'accerciser', cursor=1",
     "BRAILLE LINE:  'accerciser'",
     "     VISIBLE:  'accerciser', cursor=1",
     "SPEECH OUTPUT: 'Product: multi-select List with 379 items'",
     "SPEECH OUTPUT: 'accerciser'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Next form field",
    ["KNOWN ISSUE: Something is causing us to switch to focus mode here",
     "BRAILLE LINE:  'abiscan'",
     "     VISIBLE:  'abiscan', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=1",
     "SPEECH OUTPUT: 'Component: multi-select List with 1248 items'",
     "SPEECH OUTPUT: 'abiscan'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("a"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Toggle modes",
    ["BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "10. Next form field",
    ["KNOWN ISSUE: Something is causing us to switch to focus mode here",
     "BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=1",
     "BRAILLE LINE:  '0.0.1'",
     "     VISIBLE:  '0.0.1', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=1",
     "SPEECH OUTPUT: 'Version: multi-select List with 857 items'",
     "SPEECH OUTPUT: '0.0.1'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(PauseAction(3000))

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("a"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Next form field",
    ["BRAILLE LINE:  'table cell'",
     "     VISIBLE:  'table cell', cursor=1",
     "BRAILLE LINE:  '---'",
     "     VISIBLE:  '---', cursor=1",
     "BRAILLE LINE:  '---'",
     "     VISIBLE:  '---', cursor=1",
     "SPEECH OUTPUT: 'Target Milestone: multi-select List with 555 items'",
     "SPEECH OUTPUT: '---'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Next form field",
    ["BRAILLE LINE:  'A Comment: combo box $l table cell'",
     "     VISIBLE:  ' combo box $l table cell', cursor=1",
     "BRAILLE LINE:  'A Comment: combo box $l table cell'",
     "     VISIBLE:  ' combo box $l table cell', cursor=1",
     "SPEECH OUTPUT: 'A Comment: contains the string combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "13. Next form field",
    ["BRAILLE LINE:  'A Comment: combo box $l table cell'",
     "     VISIBLE:  ' $l table cell', cursor=1",
     "BRAILLE LINE:  'A Comment: combo box $l table cell'",
     "     VISIBLE:  ' $l table cell', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "14. Next form field",
    ["BRAILLE LINE:  'Whiteboard: combo box $l table cell'",
     "     VISIBLE:  ' combo box $l table cell', cursor=1",
     "BRAILLE LINE:  'Whiteboard: combo box $l table cell'",
     "     VISIBLE:  ' combo box $l table cell', cursor=1",
     "SPEECH OUTPUT: 'Whiteboard: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "15. Next form field",
    ["BRAILLE LINE:  'Whiteboard: combo box $l table cell'",
     "     VISIBLE:  ' $l table cell', cursor=1",
     "BRAILLE LINE:  'Whiteboard: combo box $l table cell'",
     "     VISIBLE:  ' $l table cell', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "16. Next form field",
    ["BRAILLE LINE:  'Keywords:  combo box $l'",
     "     VISIBLE:  'Keywords:  combo box $l', cursor=11",
     "BRAILLE LINE:  'Keywords:  combo box $l'",
     "     VISIBLE:  'Keywords:  combo box $l', cursor=11",
     "SPEECH OUTPUT: 'Keywords: contains all of the keywords combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "17. Next form field",
    ["BRAILLE LINE:  'Keywords:  combo box $l'",
     "     VISIBLE:  'Keywords:  combo box $l', cursor=21",
     "BRAILLE LINE:  'Keywords:  combo box $l'",
     "     VISIBLE:  'Keywords:  combo box $l', cursor=21",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "18. Next form field",
    ["BRAILLE LINE:  'UNCONFIRMED'",
     "     VISIBLE:  'UNCONFIRMED', cursor=1",
     "BRAILLE LINE:  'UNCONFIRMED'",
     "     VISIBLE:  'UNCONFIRMED', cursor=1",
     "SPEECH OUTPUT: 'Status: multi-select List with 8 items'",
     "SPEECH OUTPUT: 'UNCONFIRMED'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "19. Next form field",
    ["BRAILLE LINE:  'FIXED'",
     "     VISIBLE:  'FIXED', cursor=1",
     "BRAILLE LINE:  'FIXED'",
     "     VISIBLE:  'FIXED', cursor=1",
     "SPEECH OUTPUT: 'Resolution: multi-select List with 12 items'",
     "SPEECH OUTPUT: 'FIXED'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "20. Next form field",
    ["BRAILLE LINE:  'blocker'",
     "     VISIBLE:  'blocker', cursor=1",
     "BRAILLE LINE:  'blocker'",
     "     VISIBLE:  'blocker', cursor=1",
     "SPEECH OUTPUT: 'Severity: multi-select List with 7 items'",
     "SPEECH OUTPUT: 'blocker'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "21. Next form field",
    ["BRAILLE LINE:  'Immediate'",
     "     VISIBLE:  'Immediate', cursor=1",
     "BRAILLE LINE:  'Immediate'",
     "     VISIBLE:  'Immediate', cursor=1",
     "SPEECH OUTPUT: 'Priority: multi-select List with 5 items'",
     "SPEECH OUTPUT: 'Immediate'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "22. Next form field",
    ["BRAILLE LINE:  'All'",
     "     VISIBLE:  'All', cursor=1",
     "BRAILLE LINE:  'All'",
     "     VISIBLE:  'All', cursor=1",
     "SPEECH OUTPUT: 'OS: multi-select List with 21 items'",
     "SPEECH OUTPUT: 'All'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "23. Next form field",
    ["BRAILLE LINE:  '<x> check box the bug assignee'",
     "     VISIBLE:  '<x> check box the bug assignee', cursor=1",
     "BRAILLE LINE:  '<x> check box the bug assignee'",
     "     VISIBLE:  '<x> check box the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'Email and Numbering panel'",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "24. Next form field",
    ["BRAILLE LINE:  '< > check box the reporter'",
     "     VISIBLE:  '< > check box the reporter', cursor=1",
     "BRAILLE LINE:  '< > check box the reporter'",
     "     VISIBLE:  '< > check box the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "25. Next form field",
    ["BRAILLE LINE:  '< > check box the QA contact'",
     "     VISIBLE:  '< > check box the QA contact', cursor=1",
     "BRAILLE LINE:  '< > check box the QA contact'",
     "     VISIBLE:  '< > check box the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "26. Next form field",
    ["BRAILLE LINE:  '< > check box a CC list member'",
     "     VISIBLE:  '< > check box a CC list member', cursor=1",
     "BRAILLE LINE:  '< > check box a CC list member'",
     "     VISIBLE:  '< > check box a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "27. Next form field",
    ["BRAILLE LINE:  '< > check box a commenter'",
     "     VISIBLE:  '< > check box a commenter', cursor=1",
     "BRAILLE LINE:  '< > check box a commenter'",
     "     VISIBLE:  '< > check box a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "28. Next form field",
    ["BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "SPEECH OUTPUT: 'contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "29. Next form field",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "30. Next form field",
    ["BRAILLE LINE:  '<x> check box the bug assignee'",
     "     VISIBLE:  '<x> check box the bug assignee', cursor=1",
     "BRAILLE LINE:  '<x> check box the bug assignee'",
     "     VISIBLE:  '<x> check box the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "31. Next form field",
    ["BRAILLE LINE:  '<x> check box the reporter'",
     "     VISIBLE:  '<x> check box the reporter', cursor=1",
     "BRAILLE LINE:  '<x> check box the reporter'",
     "     VISIBLE:  '<x> check box the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "32. Next form field",
    ["BRAILLE LINE:  '<x> check box the QA contact'",
     "     VISIBLE:  '<x> check box the QA contact', cursor=1",
     "BRAILLE LINE:  '<x> check box the QA contact'",
     "     VISIBLE:  '<x> check box the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "33. Next form field",
    ["BRAILLE LINE:  '<x> check box a CC list member'",
     "     VISIBLE:  '<x> check box a CC list member', cursor=1",
     "BRAILLE LINE:  '<x> check box a CC list member'",
     "     VISIBLE:  '<x> check box a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "34. Next form field",
    ["BRAILLE LINE:  '< > check box a commenter'",
     "     VISIBLE:  '< > check box a commenter', cursor=1",
     "BRAILLE LINE:  '< > check box a commenter'",
     "     VISIBLE:  '< > check box a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "35. Next form field",
    ["BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "BRAILLE LINE:  ' combo box'",
     "     VISIBLE:  ' combo box', cursor=1",
     "SPEECH OUTPUT: 'contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "36. Next form field",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "37. Next form field",
    ["BRAILLE LINE:  ' combo box bugs numbered:  $l'",
     "     VISIBLE:  ' combo box bugs numbered:  $l', cursor=1",
     "BRAILLE LINE:  ' combo box bugs numbered:  $l'",
     "     VISIBLE:  ' combo box bugs numbered:  $l', cursor=1",
     "SPEECH OUTPUT: 'Only include combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "38. Next form field",
    ["KNOWN ISSUE: We want to speak 'bugs numbered'; we're instead infering the text below.",
     "BRAILLE LINE:  ' combo box bugs numbered:  $l'",
     "     VISIBLE:  ' combo box bugs numbered:  $l', cursor=27",
     "BRAILLE LINE:  ' combo box bugs numbered:  $l'",
     "     VISIBLE:  ' combo box bugs numbered:  $l', cursor=27",
     "SPEECH OUTPUT: '(comma-separated list) entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "39. Next form field",
    ["KNOWN ISSUE: Another case where we want to speak 'Only bugs changed between' before the entry.",
     "BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=1",
     "BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=1",
     "SPEECH OUTPUT: 'Bug Changes panel'",
     "SPEECH OUTPUT: '(YYYY-MM-DD or relative dates) entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "40. Next form field",
    ["KNOWN ISSUE: Another case of infering the text below rather than text before, i.e. 'and'.",
     "BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=9",
     "BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=9",
     "SPEECH OUTPUT: '(YYYY-MM-DD or relative dates) entry Now'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "41. Next form field",
    ["BRAILLE LINE:  '[Bug creation]'",
     "     VISIBLE:  '[Bug creation]', cursor=1",
     "BRAILLE LINE:  '[Bug creation]'",
     "     VISIBLE:  '[Bug creation]', cursor=1",
     "SPEECH OUTPUT: 'where one or more of the following changed: multi-select List with 26 items'",
     "SPEECH OUTPUT: '[Bug creation]'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "42. Next form field",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'and the new value was: entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "43. Next form field",
    ["BRAILLE LINE:  'Unspecified'",
     "     VISIBLE:  'Unspecified', cursor=1",
     "BRAILLE LINE:  'Unspecified'",
     "     VISIBLE:  'Unspecified', cursor=1",
     "SPEECH OUTPUT: 'GNOME version: multi-select List with 14 items'",
     "SPEECH OUTPUT: 'Unspecified'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "44. Next form field",
    ["BRAILLE LINE:  'Unspecified'",
     "     VISIBLE:  'Unspecified', cursor=1",
     "BRAILLE LINE:  'Unspecified'",
     "     VISIBLE:  'Unspecified', cursor=1",
     "SPEECH OUTPUT: 'GNOME target: multi-select List with 12 items'",
     "SPEECH OUTPUT: 'Unspecified'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "45. Next form field",
    ["BRAILLE LINE:  'Sort results by:  combo box'",
     "     VISIBLE:  'Sort results by:  combo box', cursor=18",
     "BRAILLE LINE:  'Sort results by:  combo box'",
     "     VISIBLE:  'Sort results by:  combo box', cursor=18",
     "SPEECH OUTPUT: 'Sort results by: Reuse same sort as last time combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "46. Next form field",
    ["BRAILLE LINE:  'Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "BRAILLE LINE:  'Search push button'",
     "     VISIBLE:  'Search push button', cursor=1",
     "SPEECH OUTPUT: 'Search push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "47. Next form field",
    ["KNOWN ISSUE: Should the checkbox indicator be where it is physically or by the role?",
     "BRAILLE LINE:  '     and remember these as my default search options < > check box'",
     "     VISIBLE:  '< > check box', cursor=1",
     "BRAILLE LINE:  '     and remember these as my default search options < > check box'",
     "     VISIBLE:  '< > check box', cursor=1",
     "SPEECH OUTPUT: 'and remember these as my default search options check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "48. Next form field",
    ["BRAILLE LINE:  '< > check box Not (negate this whole chart)'",
     "     VISIBLE:  '< > check box Not (negate this w', cursor=1",
     "BRAILLE LINE:  '< > check box Not (negate this whole chart)'",
     "     VISIBLE:  '< > check box Not (negate this w', cursor=1",
     "SPEECH OUTPUT: 'Not (negate this whole chart) check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "49. Next form field",
    ["BRAILLE LINE:  ' combo box  combo box  $l Or push button'",
     "     VISIBLE:  ' combo box  combo box  $l Or pus', cursor=1",
     "BRAILLE LINE:  ' combo box  combo box  $l Or push button'",
     "     VISIBLE:  ' combo box  combo box  $l Or pus', cursor=1",
     "SPEECH OUTPUT: '--- combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "50. Next form field",
    ["BRAILLE LINE:  ' combo box   $l combo box'",
     "     VISIBLE:  ' combo box   $l combo box', cursor=16",
     "BRAILLE LINE:  ' combo box   $l combo box'",
     "     VISIBLE:  ' combo box   $l combo box', cursor=16",
     "SPEECH OUTPUT: '--- combo box'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
