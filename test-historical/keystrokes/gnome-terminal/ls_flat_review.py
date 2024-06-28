#!/usr/bin/python

import os

from macaroon.playback import *
import utils

tmpdir = "/tmp/gnome-terminal-wd"
for i in range(10):
    filename = os.path.join(tmpdir, "another_test_file_%s" % i)
    os.close(os.open(filename, os.O_CREAT, 0o700))

sequence = MacroSequence()
sequence.append(PauseAction(3000))
sequence.append(TypeAction("ls"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line",
    ["BRAILLE LINE:  '$  $l'",
     "     VISIBLE:  '$  $l', cursor=3",
     "SPEECH OUTPUT: '$ ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "2. Review previous line",
    ["BRAILLE LINE:  'another_test_file_3  another_test_file_7 $l'",
     "     VISIBLE:  'another_test_file_3  another_tes', cursor=1",
     "SPEECH OUTPUT: 'another_test_file_3  another_test_file_7",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "3. Review previous line",
    ["BRAILLE LINE:  'another_test_file_2  another_test_file_6 $l'",
     "     VISIBLE:  'another_test_file_2  another_tes', cursor=1",
     "SPEECH OUTPUT: 'another_test_file_2  another_test_file_6",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "4. Review previous line",
    ["BRAILLE LINE:  'another_test_file_1  another_test_file_5  another_test_file_9 $l'",
     "     VISIBLE:  'another_test_file_1  another_tes', cursor=1",
     "SPEECH OUTPUT: 'another_test_file_1  another_test_file_5  another_test_file_9",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous line",
    ["BRAILLE LINE:  'another_test_file_0  another_test_file_4  another_test_file_8 $l'",
     "     VISIBLE:  'another_test_file_0  another_tes', cursor=1",
     "SPEECH OUTPUT: 'another_test_file_0  another_test_file_4  another_test_file_8",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  'another_test_file_1  another_test_file_5  another_test_file_9 $l'",
     "     VISIBLE:  'another_test_file_1  another_tes', cursor=1",
     "SPEECH OUTPUT: 'another_test_file_1  another_test_file_5  another_test_file_9",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Review first line",
    ["BRAILLE LINE:  'File Edit View Search Terminal Help $l'",
     "     VISIBLE:  'File Edit View Search Terminal H', cursor=1",
     "SPEECH OUTPUT: 'File Edit View Search Terminal Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next line",
    ["BRAILLE LINE:  '$ ls $l'",
     "     VISIBLE:  '$ ls $l', cursor=1",
     "SPEECH OUTPUT: '$ ls",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next line",
    ["BRAILLE LINE:  'another_test_file_0  another_test_file_4  another_test_file_8 $l'",
     "     VISIBLE:  'another_test_file_0  another_tes', cursor=1",
     "SPEECH OUTPUT: 'another_test_file_0  another_test_file_4  another_test_file_8",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Review last line",
    ["KNOWN ISSUE: We're not finding the bottom",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "12. Review previous line",
    ["KNOWN ISSUE: We're not finding the bottom",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
