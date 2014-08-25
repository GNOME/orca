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
    ["BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  ' $l text field using default typ', cursor=1",
     "SPEECH OUTPUT: 'Enter your Name: entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Next form field",
    ["BRAILLE LINE:  '1. Enter your Address:  $l text field using SIZE and'",
     "     VISIBLE:  ' $l text field using SIZE and', cursor=1",
     "SPEECH OUTPUT: '1. Enter your Address: entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l image text field using'",
     "     VISIBLE:  ' $l 3. Enter your State:  $l 4. ', cursor=1",
     "SPEECH OUTPUT: '2. Enter your City: entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l image text field using'",
     "     VISIBLE:  ' $l 4. Enter your Country: US $l', cursor=1",
     "SPEECH OUTPUT: '3. Enter your State: entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l image text field using'",
     "     VISIBLE:  'US $l image text field using', cursor=1",
     "SPEECH OUTPUT: '4. Enter your Country: entry US'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Next form field",
    ["BRAILLE LINE:  '5. Enter your Zip:  $l'",
     "     VISIBLE:  '5. Enter your Zip:  $l', cursor=20",
     "SPEECH OUTPUT: '5. Enter your Zip: entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Next form field",
    ["BRAILLE LINE:  'character:  $l'",
     "     VISIBLE:  'character:  $l', cursor=12",
     "SPEECH OUTPUT: 'character: entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Next form field",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  '< > check box bird'",
     "     VISIBLE:  '< > check box bird', cursor=1",
     "SPEECH OUTPUT: 'check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Next form field",
    ["BRAILLE LINE:  '< > check box fish'",
     "     VISIBLE:  '< > check box fish', cursor=1",
     "SPEECH OUTPUT: 'fish check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "10. Next form field",
    ["KNOWN ISSUE: We are treating the separator as if it is on the same line",
     "BRAILLE LINE:  '< > check box wild animal separator'",
     "     VISIBLE:  '< > check box wild animal separa', cursor=1",
     "SPEECH OUTPUT: 'wild animal check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Next form field",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  '&=y radio button cabernet sauvignon'",
     "     VISIBLE:  '&=y radio button cabernet sauvig', cursor=1",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Next form field",
    ["BRAILLE LINE:  '& y radio button merlot'",
     "     VISIBLE:  '& y radio button merlot', cursor=1",
     "SPEECH OUTPUT: 'merlot not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "13. Next form field",
    ["BRAILLE LINE:  '& y radio button nebbiolo'",
     "     VISIBLE:  '& y radio button nebbiolo', cursor=1",
     "SPEECH OUTPUT: 'nebbiolo not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "14. Next form field",
    ["BRAILLE LINE:  '& y radio button pinot noir'",
     "     VISIBLE:  '& y radio button pinot noir', cursor=1",
     "SPEECH OUTPUT: 'pinot noir not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "15. Next form field",
    ["BRAILLE LINE:  '& y radio button don't drink wine'",
     "     VISIBLE:  '& y radio button don't drink win', cursor=1",
     "SPEECH OUTPUT: 'don't drink wine not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "16. Next form field",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  ' $l text field using default typ', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'Enter your Name: entry'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
