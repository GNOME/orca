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
    ["BRAILLE LINE:  'MathML test cases with scripts'",
     "     VISIBLE:  'MathML test cases with scripts', cursor=1",
     "SPEECH OUTPUT: 'MathML test cases with scripts'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'subscript b.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'superscript b.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'subscript b.'",
     "SPEECH OUTPUT: 'superscript c.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'underscript b.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'overscript b.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'underscript b.'",
     "SPEECH OUTPUT: 'overscript c.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'pre-subscript d'",
     "SPEECH OUTPUT: 'pre-superscript e'",
     "SPEECH OUTPUT: 'subscript b'",
     "SPEECH OUTPUT: 'superscript c'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'subscript b'",
     "SPEECH OUTPUT: 'superscript c'",
     "SPEECH OUTPUT: 'subscript d'",
     "SPEECH OUTPUT: 'superscript e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'pre-subscript b'",
     "SPEECH OUTPUT: 'pre-superscript c'",
     "SPEECH OUTPUT: 'pre-subscript d'",
     "SPEECH OUTPUT: 'pre-superscript e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'pre-subscript e'",
     "SPEECH OUTPUT: 'pre-superscript f'",
     "SPEECH OUTPUT: 'pre-superscript g'",
     "SPEECH OUTPUT: 'subscript b'",
     "SPEECH OUTPUT: 'subscript c'",
     "SPEECH OUTPUT: 'superscript d'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'End of test'",
     "     VISIBLE:  'End of test', cursor=1",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
