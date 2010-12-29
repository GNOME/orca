# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output of Firefox on GNOME bugzilla's form
for entering bugs. 
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

sequence.append(TypeAction(utils.htmlURLPrefix + "enter-bug-form.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Enter Bug: orca",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Home Image Bugzilla New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'Home Image Bugzilla New bug · Br', cursor=1",
     "SPEECH OUTPUT: 'Home link image Bugzilla New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Home link image'",
     "SPEECH OUTPUT: 'Bugzilla New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'",
     "SPEECH OUTPUT: 'Enter Bug: orca – This page lets you enter a new bug into Bugzilla. heading level 1'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the bug writing guidelines link , please look at the list of most frequently reported bugs link , and please search link  or browse link  for the bug.'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Reporter:'",
     "SPEECH OUTPUT: 'joanmarie.diggs@gmail.com'",
     "SPEECH OUTPUT: 'Product:'",
     "SPEECH OUTPUT: 'orca'",
     "SPEECH OUTPUT: 'Version:'",
     "SPEECH OUTPUT: '2.21.x List with 9 items'",
     "SPEECH OUTPUT: 'Component link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'braille List with 5 items'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'GNOME version link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'Unspecified combo box'",
     "SPEECH OUTPUT: 'OS link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'Linux combo box'",
     "SPEECH OUTPUT: 'Severity link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'normal combo box'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Summary:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Description:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Optional Fields'",
     "SPEECH OUTPUT: 'Cc:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Keywords link'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Depends on:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Blocks:'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: '   Commit button'",
     "SPEECH OUTPUT: '      Remember values as bookmarkable template button'",
     "SPEECH OUTPUT: '",
     "We've made a guess at your operating system. Please check it and, if we got it wrong, email bugmaster@gnome.org.'",
     "SPEECH OUTPUT: 'Saved Searches: All Orca link  | Firefox link  | open orca link  | Open RFEs link'"]))

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
