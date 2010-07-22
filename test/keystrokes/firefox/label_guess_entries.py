# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of entries test page.  Note that not
all of these are "right"/ideal. But this is the current status quo for
regression testing.  We can revisit/refine the guessing heuristics over
time and based upon feedback.
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

sequence.append(TypeAction(utils.htmlURLPrefix + "entries.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Here are some entries h2'",
     "     VISIBLE:  'Here are some entries h2', cursor=1",
     "SPEECH OUTPUT: 'Here are some entries heading level 2'"]))

########################################################################
# Press Insert+Tab to move from form field to form field.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Type something rather amusing here: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Amusing numbers fall between  $l and  $l .'",
     "     VISIBLE:  ' $l and  $l .', cursor=1",
     "SPEECH OUTPUT: 'Amusing numbers fall between text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Amusing numbers fall between  $l and  $l .'",
     "     VISIBLE:  ' $l .', cursor=1",
     "SPEECH OUTPUT: 'and text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l I'm a label'",
     "     VISIBLE:  ' $l I'm a label', cursor=1",
     "SPEECH OUTPUT: 'I'm a label text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l Am I a label as well?'",
     "     VISIBLE:  ' $l Am I a label as well?', cursor=1",
     "SPEECH OUTPUT: 'Am I a label as well? text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l Too far away to be a label.'",
     "     VISIBLE:  ' $l Too far away to be a label.', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Distance doesn't count on the left $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Distance doesn't count on the left text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'First Name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'M.I. text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Last Name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First Name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BUG? - We're now only guessing the previous line and not the entire field.",
     "BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'initial text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'Given name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Surname text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=10",
     "SPEECH OUTPUT: 'patched image text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=10",
     "SPEECH OUTPUT: 'patched image text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=10",
     "SPEECH OUTPUT: 'patched image text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'bandaid graphic Image $l'",
     "     VISIBLE:  'bandaid graphic Image $l', cursor=22",
     "SPEECH OUTPUT: 'bandaid graphic text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  ' $l bandaid graphic redux Image'",
     "     VISIBLE:  ' $l bandaid graphic redux Image', cursor=1",
     "SPEECH OUTPUT: 'bandaid graphic redux text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Magic disappearing text trick: $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Magic disappearing text trick:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Magic disappearing text trick: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Tell me a secret:  $l'",
     "     VISIBLE:  'Tell me a secret:  $l', cursor=19",
     "SPEECH OUTPUT: 'Tell me a secret: password'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'I $l'",
     "     VISIBLE:  'I $l', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself: text'",
     "SPEECH OUTPUT: 'I' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'Type something rather amusing here: text'"]))

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
