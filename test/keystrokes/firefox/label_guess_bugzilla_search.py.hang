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
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

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
    ["BRAILLE LINE:  'Home Image Bugzilla New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'Home Image Bugzilla New bug · Br', cursor=1",
     "BRAILLE LINE:  'Home Image Bugzilla New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'Home Image Bugzilla New bug · Br', cursor=1",
     "SPEECH OUTPUT: 'Home link image'"]))

########################################################################
# Press Insert+Tab to move from form field to form field.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo $l Search Button'",
     "     VISIBLE:  'contains all of the words/string', cursor=1",
     "SPEECH OUTPUT: 'Summary: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo $l Search Button'",
     "     VISIBLE:  ' $l Search Button', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo $l Search Button'",
     "     VISIBLE:  'Search Button', cursor=1",
     "SPEECH OUTPUT: 'Search button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["KNOWN ISSUE - Something is making this test stall here."]))
#    ["BRAILLE LINE:  'Classification: Admin List'",
#     "     VISIBLE:  'Classification: Admin List', cursor=17",
#     "SPEECH OUTPUT: 'Classification: Admin multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["KNOWN ISSUE - Something is making this test stall here."]))
#    ["BRAILLE LINE:  'Product: accerciser List'",
#     "     VISIBLE:  'Product: accerciser List', cursor=10",
#     "SPEECH OUTPUT: 'Product: accerciser multi-select List with 379 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Component: abiscan List'",
     "     VISIBLE:  'Component: abiscan List', cursor=12",
     "SPEECH OUTPUT: 'Component: abiscan multi-select List with 1248 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Version: 0.0.1 List'",
     "     VISIBLE:  'Version: 0.0.1 List', cursor=10",
     "SPEECH OUTPUT: 'Version: 0.0.1 multi-select List with 857 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Target Milestone: --- List'",
     "     VISIBLE:  'Target Milestone: --- List', cursor=19",
     "SPEECH OUTPUT: 'Target Milestone: --- multi-select List with 555 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'A Comment: contains the string Combo $l'",
     "     VISIBLE:  'contains the string Combo $l', cursor=1",
     "SPEECH OUTPUT: 'A Comment: contains the string combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'A Comment: contains the string Combo $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Whiteboard: contains all of the words/strings Combo $l'",
     "     VISIBLE:  'contains all of the words/string', cursor=1",
     "SPEECH OUTPUT: 'Whiteboard: contains all of the words/strings combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Whiteboard: contains all of the words/strings Combo $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Keywords: contains all of the keywords Combo $l'",
     "     VISIBLE:  'contains all of the keywords Com', cursor=1",
     "SPEECH OUTPUT: 'Keywords: contains all of the keywords combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Keywords: contains all of the keywords Combo $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Status: UNCONFIRMED List'",
     "     VISIBLE:  'Status: UNCONFIRMED List', cursor=9",
     "SPEECH OUTPUT: 'Status: UNCONFIRMED multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Resolution: FIXED List'",
     "     VISIBLE:  'Resolution: FIXED List', cursor=13",
     "SPEECH OUTPUT: 'Resolution: FIXED multi-select List with 12 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Severity: blocker List'",
     "     VISIBLE:  'Severity: blocker List', cursor=11",
     "SPEECH OUTPUT: 'Severity: blocker multi-select List with 7 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Priority: Immediate List'",
     "     VISIBLE:  'Priority: Immediate List', cursor=11",
     "SPEECH OUTPUT: 'Priority: Immediate multi-select List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'OS: All List'",
     "     VISIBLE:  'OS: All List', cursor=5",
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
     "SPEECH OUTPUT: 'contains combo box'"]))

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
     "SPEECH OUTPUT: 'contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
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
     "SPEECH OUTPUT: 'Only include combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Only include Combo bugs numbered:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'bugs numbered: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BUG? - Looks like we are no longer guessing the correct thing.",
     "BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=1",
     "SPEECH OUTPUT: 'Email and Numbering text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=9",
     "SPEECH OUTPUT: 'and text Now'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Email and Numbering [Bug creation] List'",
     "     VISIBLE:  'Email and Numbering [Bug creatio', cursor=21",
     "SPEECH OUTPUT: 'Email and Numbering [Bug creation] multi-select List with 26 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BUG? - Looks like we are no longer guessing the correct thing.",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Email and Numbering text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'GNOME version: Unspecified List'",
     "     VISIBLE:  'GNOME version: Unspecified List', cursor=16",
     "SPEECH OUTPUT: 'GNOME version: Unspecified multi-select List with 14 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'GNOME target: Unspecified List'",
     "     VISIBLE:  'GNOME target: Unspecified List', cursor=15",
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
     "SPEECH OUTPUT: 'Sort results by: Reuse same sort as last time combo box'"]))

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
    ["BRAILLE LINE:  '    < > CheckBox and remember these as my default search options'",
     "     VISIBLE:  '< > CheckBox and remember these ', cursor=1",
     "SPEECH OUTPUT: 'and remember these as my default search options check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox Not (negate this whole chart)'",
     "     VISIBLE:  '< > CheckBox Not \(negate this wh', cursor=1",
     "SPEECH OUTPUT: 'Not (negate this whole chart) check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '--- Combo --- Combo  $l Or Button'",
     "     VISIBLE:  '--- Combo --- Combo  $l Or Butto', cursor=1",
     "SPEECH OUTPUT: '--- combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '--- Combo --- Combo  $l Or Button'",
     "     VISIBLE:  '--- Combo  $l Or Button', cursor=1",
     "SPEECH OUTPUT: '--- combo box'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
