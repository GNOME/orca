#!/usr/bin/python

"""Test of label guess functionality."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Next form field",
    ["BRAILLE LINE:  'Enter your Name:  $l'",
     "     VISIBLE:  'Enter your Name:  $l', cursor=17",
     "SPEECH OUTPUT: 'Enter your Name: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Next form field",
    ["BRAILLE LINE:  '1. Enter your Address:  $l'",
     "     VISIBLE:  '1. Enter your Address:  $l', cursor=23",
     "SPEECH OUTPUT: '1. Enter your Address: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l'",
     "     VISIBLE:  '2. Enter your City:  $l', cursor=20",
     "SPEECH OUTPUT: '2. Enter your City: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Next form field",
    ["BRAILLE LINE:  '3. Enter your State:  $l'",
     "     VISIBLE:  '3. Enter your State:  $l', cursor=21",
     "SPEECH OUTPUT: '3. Enter your State: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Next form field",
    ["BRAILLE LINE:  '4. Enter your Country: US $l'",
     "     VISIBLE:  '4. Enter your Country: US $l', cursor=24",
     "SPEECH OUTPUT: '4. Enter your Country: entry'",
     "SPEECH OUTPUT: 'US.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Next form field",
    ["BRAILLE LINE:  '5. Enter your Zip:  $l'",
     "     VISIBLE:  '5. Enter your Zip:  $l', cursor=19",
     "SPEECH OUTPUT: '5. Enter your Zip: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Next form field",
    ["BRAILLE LINE:  'character:  $l'",
     "     VISIBLE:  'character:  $l', cursor=11",
     "SPEECH OUTPUT: 'character: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Next form field",
    ["BRAILLE LINE:  '< > bird check box'",
     "     VISIBLE:  '< > bird check box', cursor=1",
     "SPEECH OUTPUT: 'bird check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Next form field",
    ["BRAILLE LINE:  '< > fish check box'",
     "     VISIBLE:  '< > fish check box', cursor=1",
     "SPEECH OUTPUT: 'fish check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "10. Next form field",
    ["BRAILLE LINE:  '< > wild animal check box'",
     "     VISIBLE:  '< > wild animal check box', cursor=1",
     "SPEECH OUTPUT: 'wild animal check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Next form field",
    ["BRAILLE LINE:  '&=y cabernet sauvignon radio button'",
     "     VISIBLE:  '&=y cabernet sauvignon radio but', cursor=1",
     "SPEECH OUTPUT: 'cabernet sauvignon.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Next form field",
    ["BRAILLE LINE:  '& y merlot radio button'",
     "     VISIBLE:  '& y merlot radio button', cursor=1",
     "SPEECH OUTPUT: 'merlot.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "13. Next form field",
    ["BRAILLE LINE:  '& y nebbiolo radio button'",
     "     VISIBLE:  '& y nebbiolo radio button', cursor=1",
     "SPEECH OUTPUT: 'nebbiolo.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "14. Next form field",
    ["BRAILLE LINE:  '& y pinot noir radio button'",
     "     VISIBLE:  '& y pinot noir radio button', cursor=1",
     "SPEECH OUTPUT: 'pinot noir.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "15. Next form field",
    ["BRAILLE LINE:  '& y don't drink wine radio button'",
     "     VISIBLE:  '& y don't drink wine radio butto', cursor=1",
     "SPEECH OUTPUT: 'don't drink wine.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "16. Next form field",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Enter your Name:  $l'",
     "     VISIBLE:  'Enter your Name:  $l', cursor=17",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'Enter your Name: entry.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
