#!/usr/bin/python

"""Test of label guess functionality."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Next form field",
    ["BRAILLE LINE:  'search mozilla:  $l Go push button'",
     "     VISIBLE:  'search mozilla:  $l Go push butt', cursor=0",
     "SPEECH OUTPUT: 'search mozilla:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Next form field",
    ["KNOWN ISSUE: We are not scrolling to the current item",
     "BRAILLE LINE:  'search mozilla:  $l Go push button'",
     "     VISIBLE:  'search mozilla:  $l Go push butt', cursor=0",
     "SPEECH OUTPUT: 'Go'",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Next form field",
    ["BRAILLE LINE:  'Your email address: $l'",
     "     VISIBLE:  'Your email address: $l', cursor=0",
     "SPEECH OUTPUT: 'Your email address:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Next form field",
    ["BRAILLE LINE:  'Your name (optional): $l'",
     "     VISIBLE:  'Your name (optional): $l', cursor=0",
     "SPEECH OUTPUT: 'Your name (optional):'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Next form field",
    ["BRAILLE LINE:  'Pick a password: $l'",
     "     VISIBLE:  'Pick a password: $l', cursor=0",
     "SPEECH OUTPUT: 'Pick a password:'",
     "SPEECH OUTPUT: 'password text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Next form field",
    ["BRAILLE LINE:  'Reenter password to confirm: $l'",
     "     VISIBLE:  'Reenter password to confirm: $l', cursor=0",
     "SPEECH OUTPUT: 'Reenter password to confirm:'",
     "SPEECH OUTPUT: 'password text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Next form field",
    ["BRAILLE LINE:  '&=y radio button No & y radio button Yes'",
     "     VISIBLE:  '&=y radio button No & y radio bu', cursor=0",
     "SPEECH OUTPUT: 'No'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Next form field",
    ["BRAILLE LINE:  '&=y radio button No & y radio button Yes'",
     "     VISIBLE:  '&=y radio button No & y radio bu', cursor=0",
     "SPEECH OUTPUT: 'Yes'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Next form field",
    ["BRAILLE LINE:  'Subscribe push button'",
     "     VISIBLE:  'Subscribe push button', cursor=0",
     "SPEECH OUTPUT: 'Subscribe",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "10. Next form field",
    ["BRAILLE LINE:  'Admin address:  $l Password:  $l Visit Subscriber List push button'",
     "     VISIBLE:  'Admin address:  $l Password:  $l', cursor=0",
     "SPEECH OUTPUT: 'Admin address:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Next form field",
    ["BRAILLE LINE:  'Admin address:  $l Password:  $l Visit Subscriber List push button'",
     "     VISIBLE:  'Admin address:  $l Password:  $l', cursor=0",
     "SPEECH OUTPUT: 'Password:'",
     "SPEECH OUTPUT: 'password text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Next form field",
    ["BRAILLE LINE:  'Admin address:  $l Password:  $l Visit Subscriber List push button'",
     "     VISIBLE:  'Admin address:  $l Password:  $l', cursor=0",
     "SPEECH OUTPUT: 'Visit Subscriber List",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "13. Next form field",
    ["KNOWN ISSUE: We are failing to infer the label",
     "BRAILLE LINE:  ' $l Unsubscribe or edit options push button'",
     "     VISIBLE:  ' $l Unsubscribe or edit options ', cursor=0",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "14. Next form field",
    ["BRAILLE LINE:  ' $l Unsubscribe or edit options push button'",
     "     VISIBLE:  ' $l Unsubscribe or edit options ', cursor=0",
     "SPEECH OUTPUT: 'Unsubscribe or edit options",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
