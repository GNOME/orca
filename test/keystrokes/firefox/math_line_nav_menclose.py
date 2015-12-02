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
    ["BRAILLE LINE:  'MathML menclose test cases'",
     "     VISIBLE:  'MathML menclose test cases', cursor=1",
     "SPEECH OUTPUT: 'MathML menclose test cases'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a long division sign'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a long division sign'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: an actuarial symbol'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a phasor angle'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a radical'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a rounded box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a circle'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a line on the left'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a line on the right'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a line at the top'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a line at the bottom'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a line on the left and a line on the right'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a line at the bottom, a line on the left, a line on the right, and, a line at the top'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: an up diagonal strike'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a down diagonal strike'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a vertical strike'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: a horizontal strike'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y Enclosed by: an arabic factorial symbol'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'End of test'",
     "     VISIBLE:  'End of test', cursor=1",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
