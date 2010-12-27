# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with empty
anchors.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "bug-517371" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-517371.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Testing",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'FAQ h1'",
     "     VISIBLE:  'FAQ h1', cursor=1",
     "SPEECH OUTPUT: 'FAQ ' voice=uppercase",
     "SPEECH OUTPUT: 'heading level 1'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. What's a battery?'",
     "     VISIBLE:  'Q. What's a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What's a battery? link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up? link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page? h2'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page? link ",
     " ",
     " heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'FOO h2'",
     "     VISIBLE:  'FOO h2', cursor=1",
     "SPEECH OUTPUT: 'FOO'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. Why would someone put a line break in a heading?'",
     "     VISIBLE:  'Q. Why would someone put a line ', cursor=1",
     "SPEECH OUTPUT: 'Q. Why would someone put a line break in a heading? link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. What is the airspeed velocity of an unladen swallow? h2'",
     "     VISIBLE:  'Q. What is the airspeed velocity', cursor=1",
     "SPEECH OUTPUT: 'Q. What is the airspeed velocity of an unladen swallow? link ",
     " ",
     " heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. What is a battery?'",
     "     VISIBLE:  'Q. What is a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What is a battery?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'A. Look it up.'",
     "     VISIBLE:  'A. Look it up.', cursor=1",
     "SPEECH OUTPUT: 'A. Look it up.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'A. That way.'",
     "     VISIBLE:  'A. That way.', cursor=1",
     "SPEECH OUTPUT: 'A. That way.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page?'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'A. Empty anchors.'",
     "     VISIBLE:  'A. Empty anchors.', cursor=1",
     "SPEECH OUTPUT: 'A. Empty anchors.'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page?'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'A. That way.'",
     "     VISIBLE:  'A. That way.', cursor=1",
     "SPEECH OUTPUT: 'A. That way.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'A. Look it up.'",
     "     VISIBLE:  'A. Look it up.', cursor=1",
     "SPEECH OUTPUT: 'A. Look it up.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. What is a battery?'",
     "     VISIBLE:  'Q. What is a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What is a battery?",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' h2'",
     "     VISIBLE:  ' h2', cursor=1",
     "SPEECH OUTPUT: '",
     " heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. What is the airspeed velocity of an unladen swallow? h2'",
     "     VISIBLE:  'Q. What is the airspeed velocity', cursor=1",
     "SPEECH OUTPUT: 'Q. What is the airspeed velocity of an unladen swallow? link ",
     "",
     " heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. Why would someone put a line break in a heading?'",
     "     VISIBLE:  'Q. Why would someone put a line ', cursor=1",
     "SPEECH OUTPUT: 'Q. Why would someone put a line break in a heading? link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'FOO h2'",
     "     VISIBLE:  'FOO h2', cursor=1",
     "SPEECH OUTPUT: 'FOO'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  ' h2'",
     "     VISIBLE:  ' h2', cursor=1",
     "SPEECH OUTPUT: '",
     " heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. Why did Orca used to get stuck on this page? h2'",
     "     VISIBLE:  'Q. Why did Orca used to get stuc', cursor=1",
     "SPEECH OUTPUT: 'Q. Why did Orca used to get stuck on this page? link ",
     " ",
     " heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. Which way is up?'",
     "     VISIBLE:  'Q. Which way is up?', cursor=1",
     "SPEECH OUTPUT: 'Q. Which way is up? link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Q. What's a battery?'",
     "     VISIBLE:  'Q. What's a battery?', cursor=1",
     "SPEECH OUTPUT: 'Q. What's a battery? link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Battery h2'",
     "     VISIBLE:  'Battery h2', cursor=1",
     "SPEECH OUTPUT: 'Battery heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'FAQ h1'",
     "     VISIBLE:  'FAQ h1', cursor=1",
     "SPEECH OUTPUT: 'FAQ '",
     "SPEECH OUTPUT: 'heading level 1'"]))

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
