#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'MathML table test cases (beyond all the torture-test test cases)'",
     "     VISIBLE:  'MathML table test cases (beyond ', cursor=1",
     "SPEECH OUTPUT: 'MathML table test cases (beyond all the torture-test test cases)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'math table with 2 rows 3 columns.'",
     "SPEECH OUTPUT: 'row 1.'",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'b.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'row 2.'",
     "SPEECH OUTPUT: 'd.'",
     "SPEECH OUTPUT: 'e.'",
     "SPEECH OUTPUT: 'f.'",
     "SPEECH OUTPUT: 'table end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'End of test'",
     "     VISIBLE:  'End of test', cursor=1",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
