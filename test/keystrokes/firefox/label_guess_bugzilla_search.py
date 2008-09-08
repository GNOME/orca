# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on bugzilla's advanced
search page.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bugzilla-advanced.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Search for bugs",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Orca+Right to get out of the focused entry, then Control+Home
# to move to the top.
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Home Link Image Bugzilla'",
     "     VISIBLE:  'Home Link Image Bugzilla', cursor=1",
     "SPEECH OUTPUT: 'Home link image Bugzilla'"]))

########################################################################
# Press Insert+Tab to move from form field to form field.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo  $l Search Button'",
     "     VISIBLE:  'contains all of the words/string', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Summary: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo  $l Search Button'",
     "     VISIBLE:  ' $l Search Button', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo  $l Search Button'",
     "     VISIBLE:  'Search Button', cursor=1",
     "SPEECH OUTPUT: 'Search button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Admin List'",
     "     VISIBLE:  'Admin List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Classification: Admin multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'accerciser List'",
     "     VISIBLE:  'accerciser List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Product: accerciser multi-select List with 379 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'abiscan List'",
     "     VISIBLE:  'abiscan List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Component abiscan multi-select List with 1248 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '0.0.1 List'",
     "     VISIBLE:  '0.0.1 List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Version: 0.0.1 multi-select List with 857 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '--- List'",
     "     VISIBLE:  '--- List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Target Milestone: --- multi-select List with 555 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'A Comment: contains the string Combo  $l'",
     "     VISIBLE:  'contains the string Combo  $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'A Comment: contains the string combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'A Comment: contains the string Combo  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Whiteboard: contains all of the words/strings Combo  $l'",
     "     VISIBLE:  'contains all of the words/string', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Whiteboard: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Whiteboard: contains all of the words/strings Combo  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Keywords Link : contains all of the keywords Combo  $l'",
     "     VISIBLE:  'contains all of the keywords Com', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Keywords contains all of the keywords combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Keywords Link : contains all of the keywords Combo  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'UNCONFIRMED List'",
     "     VISIBLE:  'UNCONFIRMED List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Status: UNCONFIRMED multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'FIXED List'",
     "     VISIBLE:  'FIXED List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Resolution: FIXED multi-select List with 12 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'blocker List'",
     "     VISIBLE:  'blocker List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Severity: blocker multi-select List with 7 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Immediate List'",
     "     VISIBLE:  'Immediate List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Priority: Immediate multi-select List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'All List'",
     "     VISIBLE:  'All List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'OS: All multi-select List with 21 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '<x> CheckBox the bug assignee'",
     "     VISIBLE:  '<x> CheckBox the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox the reporter'",
     "     VISIBLE:  '< > CheckBox the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox the QA contact'",
     "     VISIBLE:  '< > CheckBox the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox a CC list member'",
     "     VISIBLE:  '< > CheckBox a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox a commenter'",
     "     VISIBLE:  '< > CheckBox a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'contains Combo'",
     "     VISIBLE:  'contains Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'a commenter contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '<x> CheckBox the bug assignee'",
     "     VISIBLE:  '<x> CheckBox the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '<x> CheckBox the reporter'",
     "     VISIBLE:  '<x> CheckBox the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '<x> CheckBox the QA contact'",
     "     VISIBLE:  '<x> CheckBox the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '<x> CheckBox a CC list member'",
     "     VISIBLE:  '<x> CheckBox a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox a commenter'",
     "     VISIBLE:  '< > CheckBox a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'contains Combo'",
     "     VISIBLE:  'contains Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'a commenter contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Only include Combo bugs numbered:  $l'",
     "     VISIBLE:  'Only include Combo bugs numbered', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Only include combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Only include Combo bugs numbered:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'bugs numbered: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=1",
     "SPEECH OUTPUT: 'Only bugs changed between: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l  and Now $l'",
     "     VISIBLE:  ' $l  and Now $l', cursor=10",
     "SPEECH OUTPUT: 'and text Now'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '[Bug creation] List'",
     "     VISIBLE:  '[Bug creation] List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Alias [Bug creation] multi-select List with 26 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'and the new value was: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Unspecified List'",
     "     VISIBLE:  'Unspecified List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'GNOME version: Unspecified multi-select List with 14 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Unspecified List'",
     "     VISIBLE:  'Unspecified List', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'GNOME target: Unspecified multi-select List with 12 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Sort results by: Reuse same sort as last time Combo'",
     "     VISIBLE:  'Reuse same sort as last time Com', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Reuse same sort as last time combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Search Button'",
     "     VISIBLE:  'Search Button', cursor=1",
     "SPEECH OUTPUT: 'Search button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' and remember these as my default search options < > CheckBox and remember these as my default search options'",
     "     VISIBLE:  '< > CheckBox and remember these ', cursor=1",
     "SPEECH OUTPUT: 'and remember these as my default search options check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox Not (negate this whole chart)'",
     "     VISIBLE:  '< > CheckBox Not (negate this wh', cursor=1",
     "SPEECH OUTPUT: 'Not (negate this whole chart) check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '--- Combo --- Combo  $l Or Button'",
     "     VISIBLE:  '--- Combo --- Combo  $l Or Butto', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Not (negate this whole chart) --- combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '--- Combo --- Combo  $l Or Button'",
     "     VISIBLE:  '--- Combo  $l Or Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '--- combo box'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
