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
sequence.append(PauseAction(1000))

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
     "     VISIBLE:  'Home Image Bugzilla New bug', cursor=1",
     "BRAILLE LINE:  'Home Image Bugzilla New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'Home Image Bugzilla New bug', cursor=1",
     "SPEECH OUTPUT: 'Home link Image Bugzilla New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'",
     "SPEECH OUTPUT: Home link image'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' Short Bug Search Form Complicated Bug Search Form  '",
     "     VISIBLE:  ' Short Bug Search Form Complicat', cursor=1",
     "SPEECH OUTPUT: '  Short Bug Search Form link Complicated Bug Search Form  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Give me some help \(reloads page.\)'",
     "     VISIBLE:  'Give me some help \(reloads page.', cursor=1",
     "SPEECH OUTPUT: 'Give me some help link  \(reloads page.\)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo $l Search Button'",
     "     VISIBLE:  'Summary: contains all of the wor', cursor=1",
     "SPEECH OUTPUT: 'Summary: contains all of the words/strings combo box text Search button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Classification:'",
     "     VISIBLE:  'Classification:', cursor=1",
     "SPEECH OUTPUT: 'Classification:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Admin List'",
     "     VISIBLE:  'Admin List', cursor=1",
     "SPEECH OUTPUT: 'Admin multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Product:'",
     "     VISIBLE:  'Product:', cursor=1",
     "SPEECH OUTPUT: 'Product:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'accerciser List'",
     "     VISIBLE:  'accerciser List', cursor=1",
     "SPEECH OUTPUT: 'accerciser multi-select List with 379 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component link :'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'abiscan List'",
     "     VISIBLE:  'abiscan List', cursor=1",
     "SPEECH OUTPUT: 'abiscan multi-select List with 1248 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Version:'",
     "     VISIBLE:  'Version:', cursor=1",
     "SPEECH OUTPUT: 'Version:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '0.0.1 List'",
     "     VISIBLE:  '0.0.1 List', cursor=1",
     "SPEECH OUTPUT: '0.0.1 multi-select List with 857 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Target Milestone:'",
     "     VISIBLE:  'Target Milestone:', cursor=1",
     "SPEECH OUTPUT: 'Target Milestone:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '--- List'",
     "     VISIBLE:  '--- List', cursor=1",
     "SPEECH OUTPUT: '--- multi-select List with 555 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'A Comment: contains the string Combo $l'",
     "     VISIBLE:  'A Comment: contains the string C', cursor=1",
     "SPEECH OUTPUT: 'A Comment: contains the string combo box text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Whiteboard: contains all of the words/strings Combo $l'",
     "     VISIBLE:  'Whiteboard: contains all of the ', cursor=1",
     "SPEECH OUTPUT: 'Whiteboard: contains all of the words/strings combo box text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Keywords: contains all of the keywords Combo $l'",
     "     VISIBLE:  'Keywords: contains all of the ke', cursor=1",
     "SPEECH OUTPUT: 'Keywords link : contains all of the keywords combo box text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Status:'",
     "     VISIBLE:  'Status:', cursor=1",
     "SPEECH OUTPUT: 'Status:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'UNCONFIRMED List'",
     "     VISIBLE:  'UNCONFIRMED List', cursor=1",
     "SPEECH OUTPUT: 'UNCONFIRMED' voice=uppercase",
     "SPEECH OUTPUT: 'multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Resolution:'",
     "     VISIBLE:  'Resolution:', cursor=1",
     "SPEECH OUTPUT: 'Resolution:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'FIXED List'",
     "     VISIBLE:  'FIXED List', cursor=1",
     "SPEECH OUTPUT: 'FIXED' voice=uppercase",
     "SPEECH OUTPUT: 'multi-select List with 12 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Severity:'",
     "     VISIBLE:  'Severity:', cursor=1",
     "SPEECH OUTPUT: 'Severity:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'blocker List'",
     "     VISIBLE:  'blocker List', cursor=1",
     "SPEECH OUTPUT: 'blocker multi-select List with 7 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Priority:'",
     "     VISIBLE:  'Priority:', cursor=1",
     "SPEECH OUTPUT: 'Priority:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Immediate List'",
     "     VISIBLE:  'Immediate List', cursor=1",
     "SPEECH OUTPUT: 'Immediate multi-select List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'OS:'",
     "     VISIBLE:  'OS:', cursor=1",
     "SPEECH OUTPUT: 'OS:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'All List'",
     "     VISIBLE:  'All List', cursor=1",
     "SPEECH OUTPUT: 'All multi-select List with 21 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Email and Numbering'",
     "     VISIBLE:  'Email and Numbering', cursor=1",
     "SPEECH OUTPUT: 'Email and Numbering'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Any one of:'",
     "     VISIBLE:  'Any one of:', cursor=1",
     "SPEECH OUTPUT: 'Any one of:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<x> CheckBox the bug assignee'",
     "     VISIBLE:  '<x> CheckBox the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '< > CheckBox the reporter'",
     "     VISIBLE:  '< > CheckBox the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '< > CheckBox the QA contact'",
     "     VISIBLE:  '< > CheckBox the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '< > CheckBox a CC list member'",
     "     VISIBLE:  '< > CheckBox a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '< > CheckBox a commenter'",
     "     VISIBLE:  '< > CheckBox a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'contains Combo'",
     "     VISIBLE:  'contains Combo', cursor=1",
     "SPEECH OUTPUT: 'contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Any one of:'",
     "     VISIBLE:  'Any one of:', cursor=1",
     "SPEECH OUTPUT: 'Any one of:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<x> CheckBox the bug assignee'",
     "     VISIBLE:  '<x> CheckBox the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<x> CheckBox the reporter'",
     "     VISIBLE:  '<x> CheckBox the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<x> CheckBox the QA contact'",
     "     VISIBLE:  '<x> CheckBox the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '<x> CheckBox a CC list member'",
     "     VISIBLE:  '<x> CheckBox a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '< > CheckBox a commenter'",
     "     VISIBLE:  '< > CheckBox a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'contains Combo'",
     "     VISIBLE:  'contains Combo', cursor=1",
     "SPEECH OUTPUT: 'contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Only include Combo bugs numbered:  $l'",
     "     VISIBLE:  'Only include Combo bugs numbered', cursor=1",
     "SPEECH OUTPUT: 'Only include combo box bugs numbered: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '\(comma-separated list\)'",
     "     VISIBLE:  '\(comma-separated list\)', cursor=1",
     "SPEECH OUTPUT: '\(comma-separated list\)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Bug Changes'",
     "     VISIBLE:  'Bug Changes', cursor=1",
     "SPEECH OUTPUT: 'Bug Changes'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Only bugs changed between:'",
     "     VISIBLE:  'Only bugs changed between:', cursor=1",
     "SPEECH OUTPUT: 'Only bugs changed between:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=1",
     "SPEECH OUTPUT: 'Only bugs changed between: text  and text Now  ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '\(YYYY-MM-DD or relative dates\)'",
     "     VISIBLE:  '\(YYYY-MM-DD or relative dates\)', cursor=1",
     "SPEECH OUTPUT: '\(YYYY-MM-DD or relative dates\)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'where one or more of the following changed:'",
     "     VISIBLE:  'where one or more of the followi', cursor=1",
     "SPEECH OUTPUT: 'where one or more of the following changed:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '[Bug creation] List'",
     "     VISIBLE:  '[Bug creation] List', cursor=1",
     "SPEECH OUTPUT: '[Bug creation] multi-select List with 26 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'and the new value was:'",
     "     VISIBLE:  'and the new value was:', cursor=1",
     "SPEECH OUTPUT: 'and the new value was:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'and the new value was: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'GNOME version:'",
     "     VISIBLE:  'GNOME version:', cursor=1",
     "SPEECH OUTPUT: 'GNOME version:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Unspecified List'",
     "     VISIBLE:  'Unspecified List', cursor=1",
     "SPEECH OUTPUT: 'Unspecified multi-select List with 14 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'GNOME target:'",
     "     VISIBLE:  'GNOME target:', cursor=1",
     "SPEECH OUTPUT: 'GNOME target:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Unspecified List'",
     "     VISIBLE:  'Unspecified List', cursor=1",
     "SPEECH OUTPUT: 'Unspecified multi-select List with 12 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Sort results by: Reuse same sort as last time Combo'",
     "     VISIBLE:  'Sort results by: Reuse same sort', cursor=1",
     "SPEECH OUTPUT: 'Sort results by: Reuse same sort as last time combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Search Button'",
     "     VISIBLE:  'Search Button', cursor=1",
     "SPEECH OUTPUT: 'Search button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '    < > CheckBox and remember these as my default search options'",
     "     VISIBLE:  '    < > CheckBox and remember th', cursor=1",
     "SPEECH OUTPUT: '    check box not checked  and remember these as my default search options'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Advanced Searching Using Boolean Charts:'",
     "     VISIBLE:  'Advanced Searching Using Boolean', cursor=1",
     "SPEECH OUTPUT: 'Advanced Searching Using Boolean Charts:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '< > CheckBox Not \(negate this whole chart\)'",
     "     VISIBLE:  '< > CheckBox Not \(negate this wh', cursor=1",
     "SPEECH OUTPUT: 'Not (negate this whole chart) check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '--- Combo --- Combo  $l Or Button'",
     "     VISIBLE:  '--- Combo --- Combo  $l Or Butto', cursor=1",
     "SPEECH OUTPUT: '--- combo box --- combo box text Or button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'And Button       Add another boolean chart Button      '",
     "     VISIBLE:  'And Button       Add another boo', cursor=1",
     "SPEECH OUTPUT: 'And button        Add another boolean chart button       '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Saved Searches: My Bugs and Patches | All Orca | Firefox | open orca | Open RFEs'",
     "     VISIBLE:  'Saved Searches: My Bugs and Patc', cursor=1",
     "SPEECH OUTPUT: 'Saved Searches: My Bugs and Patches link  | All Orca link  | Firefox link  | open orca link  | Open RFEs link'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'And Button       Add another boolean chart Button      '",
     "     VISIBLE:  'And Button       Add another boo', cursor=1",
     "SPEECH OUTPUT: 'And button        Add another boolean chart button       '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '--- Combo --- Combo  $l Or Button'",
     "     VISIBLE:  '--- Combo --- Combo  $l Or Butto', cursor=1",
     "SPEECH OUTPUT: '--- combo box --- combo box text Or button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '< > CheckBox Not \(negate this whole chart\)'",
     "     VISIBLE:  '< > CheckBox Not \(negate this wh', cursor=1",
     "SPEECH OUTPUT: 'Not \(negate this whole chart\) check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Advanced Searching Using Boolean Charts:'",
     "     VISIBLE:  'Advanced Searching Using Boolean', cursor=1",
     "SPEECH OUTPUT: 'Advanced Searching Using Boolean Charts:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '    < > CheckBox and remember these as my default search options'",
     "     VISIBLE:  '    < > CheckBox and remember th', cursor=1",
     "SPEECH OUTPUT: '    check box not checked  and remember these as my default search options'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Search Button'",
     "     VISIBLE:  'Search Button', cursor=1",
     "SPEECH OUTPUT: 'Search button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Sort results by: Reuse same sort as last time Combo'",
     "     VISIBLE:  'Sort results by: Reuse same sort', cursor=1",
     "SPEECH OUTPUT: 'Sort results by: Reuse same sort as last time combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Unspecified List'",
     "     VISIBLE:  'Unspecified List', cursor=1",
     "SPEECH OUTPUT: 'Unspecified multi-select List with 12 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'GNOME target:'",
     "     VISIBLE:  'GNOME target:', cursor=1",
     "SPEECH OUTPUT: 'GNOME target:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Unspecified List'",
     "     VISIBLE:  'Unspecified List', cursor=1",
     "SPEECH OUTPUT: 'Unspecified multi-select List with 14 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'GNOME version:'",
     "     VISIBLE:  'GNOME version:', cursor=1",
     "SPEECH OUTPUT: 'GNOME version:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'and the new value was: text'",]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'and the new value was:'",
     "     VISIBLE:  'and the new value was:', cursor=1",
     "SPEECH OUTPUT: 'and the new value was:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '[Bug creation] List'",
     "     VISIBLE:  '[Bug creation] List', cursor=1",
     "SPEECH OUTPUT: '[Bug creation] multi-select List with 26 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'where one or more of the following changed:'",
     "     VISIBLE:  'where one or more of the followi', cursor=1",
     "SPEECH OUTPUT: 'where one or more of the following changed:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '\(YYYY-MM-DD or relative dates\)'",
     "     VISIBLE:  '\(YYYY-MM-DD or relative dates\)', cursor=1",
     "SPEECH OUTPUT: '\(YYYY-MM-DD or relative dates\)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' $l and Now $l'",
     "     VISIBLE:  ' $l and Now $l', cursor=1",
     "SPEECH OUTPUT: 'Only bugs changed between: text  and text Now ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Only bugs changed between:'",
     "     VISIBLE:  'Only bugs changed between:', cursor=1",
     "SPEECH OUTPUT: 'Only bugs changed between:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Bug Changes'",
     "     VISIBLE:  'Bug Changes', cursor=1",
     "SPEECH OUTPUT: 'Bug Changes'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '\(comma-separated list\)'",
     "     VISIBLE:  '\(comma-separated list\)', cursor=1",
     "SPEECH OUTPUT: '\(comma-separated list\)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Only include Combo bugs numbered:  $l'",
     "     VISIBLE:  'Only include Combo bugs numbered', cursor=1",
     "SPEECH OUTPUT: 'Only include combo box bugs numbered: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'contains Combo'",
     "     VISIBLE:  'contains Combo', cursor=1",
     "SPEECH OUTPUT: 'contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '< > CheckBox a commenter'",
     "     VISIBLE:  '< > CheckBox a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<x> CheckBox a CC list member'",
     "     VISIBLE:  '<x> CheckBox a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<x> CheckBox the QA contact'",
     "     VISIBLE:  '<x> CheckBox the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<x> CheckBox the reporter'",
     "     VISIBLE:  '<x> CheckBox the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<x> CheckBox the bug assignee'",
     "     VISIBLE:  '<x> CheckBox the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Any one of:'",
     "     VISIBLE:  'Any one of:', cursor=1",
     "SPEECH OUTPUT: 'Any one of:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'contains Combo'",
     "     VISIBLE:  'contains Combo', cursor=1",
     "SPEECH OUTPUT: 'contains combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '< > CheckBox a commenter'",
     "     VISIBLE:  '< > CheckBox a commenter', cursor=1",
     "SPEECH OUTPUT: 'a commenter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '< > CheckBox a CC list member'",
     "     VISIBLE:  '< > CheckBox a CC list member', cursor=1",
     "SPEECH OUTPUT: 'a CC list member check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '< > CheckBox the QA contact'",
     "     VISIBLE:  '< > CheckBox the QA contact', cursor=1",
     "SPEECH OUTPUT: 'the QA contact check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '< > CheckBox the reporter'",
     "     VISIBLE:  '< > CheckBox the reporter', cursor=1",
     "SPEECH OUTPUT: 'the reporter check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '<x> CheckBox the bug assignee'",
     "     VISIBLE:  '<x> CheckBox the bug assignee', cursor=1",
     "SPEECH OUTPUT: 'the bug assignee check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Any one of:'",
     "     VISIBLE:  'Any one of:', cursor=1",
     "SPEECH OUTPUT: 'Any one of:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Email and Numbering'",
     "     VISIBLE:  'Email and Numbering', cursor=1",
     "SPEECH OUTPUT: 'Email and Numbering'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'All List'",
     "     VISIBLE:  'All List', cursor=1",
     "SPEECH OUTPUT: 'All multi-select List with 21 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'OS:'",
     "     VISIBLE:  'OS:', cursor=1",
     "SPEECH OUTPUT: 'OS:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Immediate List'",
     "     VISIBLE:  'Immediate List', cursor=1",
     "SPEECH OUTPUT: 'Immediate multi-select List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Priority:'",
     "     VISIBLE:  'Priority:', cursor=1",
     "SPEECH OUTPUT: 'Priority:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'blocker List'",
     "     VISIBLE:  'blocker List', cursor=1",
     "SPEECH OUTPUT: 'blocker multi-select List with 7 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Severity:'",
     "     VISIBLE:  'Severity:', cursor=1",
     "SPEECH OUTPUT: 'Severity:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'FIXED List'",
     "     VISIBLE:  'FIXED List', cursor=1",
     "SPEECH OUTPUT: 'FIXED' voice=uppercase",
     "SPEECH OUTPUT: 'multi-select List with 12 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Resolution:'",
     "     VISIBLE:  'Resolution:', cursor=1",
     "SPEECH OUTPUT: 'Resolution:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'UNCONFIRMED List'",
     "     VISIBLE:  'UNCONFIRMED List', cursor=1",
     "SPEECH OUTPUT: 'UNCONFIRMED' voice=uppercase",
     "SPEECH OUTPUT: 'multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Status:'",
     "     VISIBLE:  'Status:', cursor=1",
     "SPEECH OUTPUT: 'Status:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Keywords: contains all of the keywords Combo $l'",
     "     VISIBLE:  'Keywords: contains all of the ke', cursor=1",
     "SPEECH OUTPUT: 'Keywords link : contains all of the keywords combo box text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Whiteboard: contains all of the words/strings Combo $l'",
     "     VISIBLE:  'Whiteboard: contains all of the ', cursor=1",
     "SPEECH OUTPUT: 'Whiteboard: contains all of the words/strings combo box text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'A Comment: contains the string Combo $l'",
     "     VISIBLE:  'A Comment: contains the string C', cursor=1",
     "SPEECH OUTPUT: 'A Comment: contains the string combo box text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '--- List'",
     "     VISIBLE:  '--- List', cursor=1",
     "SPEECH OUTPUT: '--- multi-select List with 555 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Target Milestone:'",
     "     VISIBLE:  'Target Milestone:', cursor=1",
     "SPEECH OUTPUT: 'Target Milestone:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '0.0.1 List'",
     "     VISIBLE:  '0.0.1 List', cursor=1",
     "SPEECH OUTPUT: '0.0.1 multi-select List with 857 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Version:'",
     "     VISIBLE:  'Version:', cursor=1",
     "SPEECH OUTPUT: 'Version:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'abiscan List'",
     "     VISIBLE:  'abiscan List', cursor=1",
     "SPEECH OUTPUT: 'abiscan multi-select List with 1248 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Component:'",
     "     VISIBLE:  'Component:', cursor=1",
     "SPEECH OUTPUT: 'Component link :'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'accerciser List'",
     "     VISIBLE:  'accerciser List', cursor=1",
     "SPEECH OUTPUT: 'accerciser multi-select List with 379 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Product:'",
     "     VISIBLE:  'Product:', cursor=1",
     "SPEECH OUTPUT: 'Product:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Admin List'",
     "     VISIBLE:  'Admin List', cursor=1",
     "SPEECH OUTPUT: 'Admin multi-select List with 8 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Classification:'",
     "     VISIBLE:  'Classification:', cursor=1",
     "SPEECH OUTPUT: 'Classification:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Summary: contains all of the words/strings Combo $l Search Button'",
     "     VISIBLE:  'Summary: contains all of the wor', cursor=1",
     "SPEECH OUTPUT: 'Summary: contains all of the words/strings combo box text Search button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Give me some help \(reloads page.\)'",
     "     VISIBLE:  'Give me some help \(reloads page.', cursor=1",
     "SPEECH OUTPUT: 'Give me some help link  \(reloads page.\)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' Short Bug Search Form Complicated Bug Search Form  '",
     "     VISIBLE:  ' Short Bug Search Form Complicat', cursor=1",
     "SPEECH OUTPUT: '  Short Bug Search Form link Complicated Bug Search Form  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Home Image Bugzilla'",
     "     VISIBLE:  'Home Image Bugzilla', cursor=1",
     "BRAILLE LINE:  'Home Image Bugzilla New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'Home Image Bugzilla New bug', cursor=1",
     "SPEECH OUTPUT: 'Home link Image Bugzilla New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'",
     "SPEECH OUTPUT: 'Home link image Bugzilla'"
     "SPEECH OUTPUT: Home link image'"]))

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
