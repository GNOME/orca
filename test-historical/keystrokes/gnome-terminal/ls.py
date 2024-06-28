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

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. ls",
    ["BRAILLE LINE:  '$ '",
     "     VISIBLE:  '$ ', cursor=3",
     "SPEECH OUTPUT: 'another_test_file_0  another_test_file_4  another_test_file_8",
     "another_test_file_1  another_test_file_5  another_test_file_9",
     "another_test_file_2  another_test_file_6",
     "another_test_file_3  another_test_file_7",
     "$ '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
