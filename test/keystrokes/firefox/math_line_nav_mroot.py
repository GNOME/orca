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
    ["BRAILLE LINE:  'MathML root test cases'",
     "     VISIBLE:  'MathML root test cases', cursor=1",
     "SPEECH OUTPUT: 'MathML root test cases'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'square root of a.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'square root of a b c.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'square root of a.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'cube root of a.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: '3 plus 4 root of a.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'fraction start.'",
     "SPEECH OUTPUT: '3 over 4.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'root of a.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'square root of b.'",
     "SPEECH OUTPUT: 'root end.'",
     "SPEECH OUTPUT: 'root of a.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'square root of fraction start.'",
     "SPEECH OUTPUT: 'a over b.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'cube root of fraction start.'",
     "SPEECH OUTPUT: 'a over b.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'c plus d root of fraction start.'",
     "SPEECH OUTPUT: 'a over b.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'b'",
     "SPEECH OUTPUT: 'root of a.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'End of test'",
     "     VISIBLE:  'End of test', cursor=1",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
