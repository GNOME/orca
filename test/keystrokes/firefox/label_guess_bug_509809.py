# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of label guess functionality, primarily by line."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "dev-accessibility.html"))
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
    ["BRAILLE LINE:  'Mozilla h1'",
     "     VISIBLE:  'Mozilla h1', cursor=1",
     "SPEECH OUTPUT: 'Mozilla link heading level 1'"]))

########################################################################
# Press Insert+Tab to move from form field to form field.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'search mozilla: search mozilla:  $l Go Button'",
     "     VISIBLE:  'search mozilla:  $l Go Button', cursor=17",
     "SPEECH OUTPUT: 'search mozilla: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'search mozilla: search mozilla:  $l Go Button'",
     "     VISIBLE:  'Go Button', cursor=1",
     "SPEECH OUTPUT: 'Go button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  'Your email address: $l '",
     "     VISIBLE:  'Your email address: $l ', cursor=20",
     "SPEECH OUTPUT: 'Your email address: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Your name (optional): $l '",
     "     VISIBLE:  'Your name (optional): $l ', cursor=22",
     "SPEECH OUTPUT: 'Your name (optional): text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Pick a password: $l '",
     "     VISIBLE:  'Pick a password: $l ', cursor=17",
     "SPEECH OUTPUT: 'Pick a password: password'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  'Reenter password to confirm: $l '",
     "     VISIBLE:  'Reenter password to confirm: $l ', cursor=29",
     "SPEECH OUTPUT: 'Reenter password to confirm: password'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'batched in a daily digest? &=y RadioButton No & y RadioButton Yes'",
     "     VISIBLE:  '&=y RadioButton No & y RadioButt', cursor=1",
     "SPEECH OUTPUT: 'No selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'batched in a daily digest? &=y RadioButton No & y RadioButton Yes'",
     "     VISIBLE:  '& y RadioButton Yes', cursor=1",
     "SPEECH OUTPUT: 'Yes not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  'Subscribe Button'",
     "     VISIBLE:  'Subscribe Button', cursor=1",
     "SPEECH OUTPUT: 'Subscribe button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Admin address:  $l Password:  $l  Visit Subscriber List Button'",
     "     VISIBLE:  ' $l Password:  $l  Visit Subscri', cursor=1",
     "SPEECH OUTPUT: 'Admin address: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Admin address:  $l Password:  $l  Visit Subscriber List Button'",
     "     VISIBLE:  ' $l  Visit Subscriber List Butto', cursor=1",
     "SPEECH OUTPUT: 'Password: password'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  'Admin address:  $l Password:  $l  Visit Subscriber List Button'",
     "     VISIBLE:  'Visit Subscriber List Button', cursor=1",
     "SPEECH OUTPUT: 'Visit Subscriber List button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  ' $l Unsubscribe or edit options Button'",
     "     VISIBLE:  ' $l Unsubscribe or edit options ', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  ' $l Unsubscribe or edit options Button'",
     "     VISIBLE:  'Unsubscribe or edit options Butt', cursor=1",
     "SPEECH OUTPUT: 'Unsubscribe or edit options button'"]))

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
