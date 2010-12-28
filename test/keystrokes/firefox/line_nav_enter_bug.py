# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on GNOME bugzilla's form
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
     "BRAILLE LINE:  'Home Image Bugzilla New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'Home Image Bugzilla New bug · Br', cursor=1",
     "SPEECH OUTPUT: 'Home link image Bugzilla New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'",
     "SPEECH OUTPUT: 'Home link image'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Enter Bug: orca – This page lets you enter a new bug into Bugzilla. h1 '",
     "     VISIBLE:  'Enter Bug: orca – This page lets', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca – This page lets you enter a new bug into Bugzilla. heading level 1 ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Before reporting a bug, please read the bug writing guidelines, please look at the list of most'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the bug writing guidelines link , please look at the list of most link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'frequently reported bugs, and please search or browse for the bug. '",
     "     VISIBLE:  'frequently reported bugs, and pl', cursor=1",
     "SPEECH OUTPUT: 'frequently reported bugs link , and please search link  or browse link  for the bug. ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Reporter: joanmarie.diggs@gmail.com Product: orca'",
     "     VISIBLE:  'Reporter: joanmarie.diggs@gmail.', cursor=1",
     "SPEECH OUTPUT: 'Reporter: joanmarie.diggs@gmail.com Product: orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Version: 2.21.x List Component: braille List'",
     "     VISIBLE:  'Version: 2.21.x List Component: ', cursor=1",
     "SPEECH OUTPUT: 'Version: 2.21.x List with 9 items Component link : braille List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'GNOME'",
     "     VISIBLE:  'GNOME', cursor=1",
     "SPEECH OUTPUT: 'GNOME link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'version:'",
     "     VISIBLE:  'version:', cursor=1",
     "SPEECH OUTPUT: 'version link :'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'GNOME Unspecified Combo'",
     "     VISIBLE:  'GNOME Unspecified Combo', cursor=7",
     "SPEECH OUTPUT: 'GNOME link Unspecified combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'OS: Linux Combo'",
     "     VISIBLE:  'OS: Linux Combo', cursor=1",
     "SPEECH OUTPUT: 'OS link : Linux combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Severity: normal Combo'",
     "     VISIBLE:  'Severity: normal Combo', cursor=1",
     "SPEECH OUTPUT: 'Severity link : normal combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Summary: $l'",
     "     VISIBLE:  'Summary: $l', cursor=1",
     "SPEECH OUTPUT: 'Summary: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Description: $l'",
     "     VISIBLE:  'Description: $l', cursor=1",
     "SPEECH OUTPUT: 'Description: text ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Optional Fields'",
     "     VISIBLE:  'Optional Fields', cursor=1",
     "SPEECH OUTPUT: 'Optional Fields'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Cc: $l'",
     "     VISIBLE:  'Cc: $l', cursor=1",
     "SPEECH OUTPUT: 'Cc: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Keywords:  $l'",
     "     VISIBLE:  'Keywords:  $l', cursor=1",
     "SPEECH OUTPUT: 'Keywords link : text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Depends on: $l'",
     "     VISIBLE:  'Depends on: $l', cursor=1",
     "SPEECH OUTPUT: 'Depends on: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Blocks: $l'",
     "     VISIBLE:  'Blocks: $l', cursor=1",
     "SPEECH OUTPUT: 'Blocks: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Commit Button      Remember values as bookmarkable template Button'",
     "     VISIBLE:  'Commit Button      Remember valu', cursor=1",
     "SPEECH OUTPUT: '   Commit button       Remember values as bookmarkable template button ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'We've made a guess at your operating system. Please check it and, if we got it wrong, email'",
     "     VISIBLE:  'We've made a guess at your opera', cursor=1",
     "SPEECH OUTPUT: 'We've made a guess at your operating system. Please check it and, if we got it wrong, email'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'bugmaster@gnome.org.'",
     "     VISIBLE:  'bugmaster@gnome.org.', cursor=1",
     "SPEECH OUTPUT: 'bugmaster@gnome.org.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Saved Searches: All Orca | Firefox | open orca | Open RFEs'",
     "     VISIBLE:  'Saved Searches: All Orca | Firef', cursor=1",
     "SPEECH OUTPUT: 'Saved Searches: All Orca link  | Firefox link  | open orca link  | Open RFEs link'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'bugmaster@gnome.org.'",
     "     VISIBLE:  'bugmaster@gnome.org.', cursor=1",
     "SPEECH OUTPUT: 'bugmaster@gnome.org.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'We've made a guess at your operating system. Please check it and, if we got it wrong, email'",
     "     VISIBLE:  'We've made a guess at your opera', cursor=1",
     "SPEECH OUTPUT: 'We've made a guess at your operating system. Please check it and, if we got it wrong, email'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Commit Button      Remember values as bookmarkable template Button'",
     "     VISIBLE:  'Commit Button      Remember valu', cursor=1",
     "SPEECH OUTPUT: '   Commit button       Remember values as bookmarkable template button ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Blocks: $l'",
     "     VISIBLE:  'Blocks: $l', cursor=1",
     "SPEECH OUTPUT: 'Blocks: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Depends on: $l'",
     "     VISIBLE:  'Depends on: $l', cursor=1",
     "SPEECH OUTPUT: 'Depends on: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Keywords:  $l'",
     "     VISIBLE:  'Keywords:  $l', cursor=1",
     "SPEECH OUTPUT: 'Keywords link : text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Cc: $l'",
     "     VISIBLE:  'Cc: $l', cursor=1",
     "SPEECH OUTPUT: 'Cc: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Optional Fields'",
     "     VISIBLE:  'Optional Fields', cursor=1",
     "SPEECH OUTPUT: 'Optional Fields'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Description: $l'",
     "     VISIBLE:  'Description: $l', cursor=1",
     "SPEECH OUTPUT: 'Description: text ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Summary: $l'",
     "     VISIBLE:  'Summary: $l', cursor=1",
     "SPEECH OUTPUT: 'Summary: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Severity: normal Combo'",
     "     VISIBLE:  'Severity: normal Combo', cursor=1",
     "SPEECH OUTPUT: 'Severity link : normal combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'OS: Linux Combo'",
     "     VISIBLE:  'OS: Linux Combo', cursor=1",
     "SPEECH OUTPUT: 'OS link : Linux combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'GNOME Unspecified Combo'",
     "     VISIBLE:  'GNOME Unspecified Combo', cursor=1",
     "SPEECH OUTPUT: 'GNOME link Unspecified combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Version: 2.21.x List Component: braille List'",
     "     VISIBLE:  'Version: 2.21.x List Component: ', cursor=1",
     "SPEECH OUTPUT: 'Version: 2.21.x List with 9 items Component link : braille List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Reporter: joanmarie.diggs@gmail.com Product: orca'",
     "     VISIBLE:  'Reporter: joanmarie.diggs@gmail.', cursor=1",
     "SPEECH OUTPUT: 'Reporter: joanmarie.diggs@gmail.com Product: orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'frequently reported bugs, and please search or browse for the bug. '",
     "     VISIBLE:  'frequently reported bugs, and pl', cursor=1",
     "SPEECH OUTPUT: 'frequently reported bugs link , and please search link  or browse link  for the bug. ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Before reporting a bug, please read the bug writing guidelines, please look at the list of most'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the bug writing guidelines link , please look at the list of most link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Enter Bug: orca – This page lets you enter a new bug into Bugzilla. h1 '",
     "     VISIBLE:  'Enter Bug: orca – This page lets', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca – This page lets you enter a new bug into Bugzilla. heading level 1 ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'New bug · Browse · Search · Repo', cursor=1",
     "SPEECH OUTPUT: 'New bug link  · Browse link  · Search link  · Reports link  · Account link  · Admin link  · Help link Logged In joanmarie.diggs@gmail.com | Log Out link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Home Image Bugzilla'",
     "     VISIBLE:  'Home Image Bugzilla', cursor=1",
     "BRAILLE LINE:  'Home Image Bugzilla New bug · Browse · Search · Reports · Account · Admin · Help Logged In joanmarie.diggs@gmail.com | Log Out'",
     "     VISIBLE:  'Home Image Bugzilla New bug · Br', cursor=1",
     "SPEECH OUTPUT: 'Home link image Bugzilla'",
     "SPEECH OUTPUT: 'Home link image'"]))

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
