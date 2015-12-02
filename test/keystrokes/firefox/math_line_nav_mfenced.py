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
    ["BRAILLE LINE:  'MathML mfenced test cases'",
     "     VISIBLE:  'MathML mfenced test cases', cursor=1",
     "SPEECH OUTPUT: 'MathML mfenced test cases'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left paren.'",
     "SPEECH OUTPUT: 'a comma.'",
     "SPEECH OUTPUT: 'b comma.'",
     "SPEECH OUTPUT: 'c comma.'",
     "SPEECH OUTPUT: 'd comma.'",
     "SPEECH OUTPUT: 'e.'",
     "SPEECH OUTPUT: 'right paren'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left brace.'",
     "SPEECH OUTPUT: 'a semicolon.'",
     "SPEECH OUTPUT: 'b semicolon.'",
     "SPEECH OUTPUT: 'c semicolon.'",
     "SPEECH OUTPUT: 'd semicolon.'",
     "SPEECH OUTPUT: 'e.'",
     "SPEECH OUTPUT: 'right brace'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left brace.'",
     "SPEECH OUTPUT: 'a semicolon.'",
     "SPEECH OUTPUT: 'b semicolon.'",
     "SPEECH OUTPUT: 'c comma.'",
     "SPEECH OUTPUT: 'd comma.'",
     "SPEECH OUTPUT: 'e.'",
     "SPEECH OUTPUT: 'right brace'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'End of test'",
     "     VISIBLE:  'End of test', cursor=1",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
