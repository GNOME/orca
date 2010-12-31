# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output of Firefox on bugzilla's advanced search page."""

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
     "SPEECH OUTPUT: 'Home link image Bugzilla New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'",
     "SPEECH OUTPUT: 'Home link image'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Home link image'",
     "SPEECH OUTPUT: 'Bugzilla New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Short Bug Search Form link'",
     "SPEECH OUTPUT: 'Complicated Bug Search Form'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Give me some help link'",
     "SPEECH OUTPUT: ' (reloads page.)'",
     "SPEECH OUTPUT: 'Summary: row header'",
     "SPEECH OUTPUT: 'contains all of the words/strings combo box'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Search button'",
     "SPEECH OUTPUT: 'Classification: column header'",
     "SPEECH OUTPUT: 'Admin multi-select List with 8 items'",
     "SPEECH OUTPUT: 'Product: column header'",
     "SPEECH OUTPUT: 'accerciser multi-select List with 379 items'",
     "SPEECH OUTPUT: 'Component link'",
     "SPEECH OUTPUT: ': column header'",
     "SPEECH OUTPUT: 'abiscan multi-select List with 1248 items'",
     "SPEECH OUTPUT: 'Version: column header'",
     "SPEECH OUTPUT: '0.0.1 multi-select List with 857 items'",
     "SPEECH OUTPUT: 'Target Milestone: column header'",
     "SPEECH OUTPUT: '--- multi-select List with 555 items'",
     "SPEECH OUTPUT: 'A Comment: row header'",
     "SPEECH OUTPUT: 'contains the string combo box'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Whiteboard: row header'",
     "SPEECH OUTPUT: 'contains all of the words/strings combo box'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Keywords link'",
     "SPEECH OUTPUT: ': row header'",
     "SPEECH OUTPUT: 'contains all of the keywords combo box'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'Status: column header'",
     "SPEECH OUTPUT: 'UNCONFIRMED NEW ASSIGNED REOPENED NEEDINFO'",
     "SPEECH OUTPUT: 'multi-select List with 8 items'",
     "SPEECH OUTPUT: 'Resolution: column header'",
     "SPEECH OUTPUT: 'FIXED'",
     "SPEECH OUTPUT: 'multi-select List with 12 items'",
     "SPEECH OUTPUT: 'Severity: column header'",
     "SPEECH OUTPUT: 'blocker multi-select List with 7 items'",
     "SPEECH OUTPUT: 'Priority: column header'",
     "SPEECH OUTPUT: 'Immediate multi-select List with 5 items'",
     "SPEECH OUTPUT: 'OS: column header'",
     "SPEECH OUTPUT: 'All multi-select List with 21 items'",
     "SPEECH OUTPUT: 'Email and Numbering'",
     "SPEECH OUTPUT: 'Any one of:'",
     "SPEECH OUTPUT: 'check box checked'",
     "SPEECH OUTPUT: ' the bug assignee'",
     "SPEECH OUTPUT: 'check box not checked'",
     "SPEECH OUTPUT: ' the reporter'",
     "SPEECH OUTPUT: 'check box not checked'",
     "SPEECH OUTPUT: ' the QA contact'",
     "SPEECH OUTPUT: 'check box not checked'",
     "SPEECH OUTPUT: ' a CC list member'",
     "SPEECH OUTPUT: 'check box not checked'",
     "SPEECH OUTPUT: ' a commenter'",
     "SPEECH OUTPUT: 'contains combo box'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Any one of:'",
     "SPEECH OUTPUT: 'check box checked'",
     "SPEECH OUTPUT: ' the bug assignee'",
     "SPEECH OUTPUT: 'check box checked'",
     "SPEECH OUTPUT: ' the reporter'",
     "SPEECH OUTPUT: 'check box checked'",
     "SPEECH OUTPUT: ' the QA contact'",
     "SPEECH OUTPUT: 'check box checked'",
     "SPEECH OUTPUT: ' a CC list member'",
     "SPEECH OUTPUT: 'check box not checked'",
     "SPEECH OUTPUT: ' a commenter'",
     "SPEECH OUTPUT: 'contains combo box'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'Only include combo box'",
     "SPEECH OUTPUT: 'bugs numbered:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: '(comma-separated list)'",
     "SPEECH OUTPUT: 'Bug Changes'",
     "SPEECH OUTPUT: '•Only bugs changed between:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: ' and text Now ",
     "(YYYY-MM-DD or relative dates)'",
     "SPEECH OUTPUT: '•where one or more of the following changed:'",
     "SPEECH OUTPUT: '[Bug creation] multi-select List with 26 items'",
     "SPEECH OUTPUT: '•and the new value was:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'GNOME version: column header'",
     "SPEECH OUTPUT: 'Unspecified multi-select List with 14 items'",
     "SPEECH OUTPUT: 'GNOME target: column header'",
     "SPEECH OUTPUT: 'Unspecified multi-select List with 12 items'",
     "SPEECH OUTPUT: 'Sort results by: Reuse same sort as last time combo box'",
     "SPEECH OUTPUT: 'Search button'",
     "SPEECH OUTPUT: '    check box not checked  and remember these as my default search options'",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'Advanced Searching Using Boolean Charts:'",
     "SPEECH OUTPUT: 'check box not checked'",
     "SPEECH OUTPUT: ' Not (negate this whole chart)'",
     "SPEECH OUTPUT: '--- combo box'",
     "SPEECH OUTPUT: '--- combo box text'",
     "SPEECH OUTPUT: 'Or button'",
     "SPEECH OUTPUT: 'And button'",
     "SPEECH OUTPUT: '       Add another boolean chart button       '",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'Saved Searches: My Bugs and Patches link  | All Orca link  | Firefox link  | open orca link  | Open RFEs link'"]))

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
