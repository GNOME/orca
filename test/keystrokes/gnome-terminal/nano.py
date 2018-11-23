#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("nano"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Launch Nano",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: '  GNU nano [\d\.]+\s+New Buffer\s*",
     "",
     "'"]))

sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("So is this."))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("Done."))
sequence.append(utils.AssertPresentationAction(
    "2.Typing text",
    ["KNOWN ISSUE: We should be able to do less braille updating here",
     "KNOWN ISSUE: We're speaking the initial D due to imperfect heuristics",
     "BRAILLE LINE:  'D'",
     "     VISIBLE:  'D', cursor=2",
     "BRAILLE LINE:  'Do'",
     "     VISIBLE:  'Do', cursor=3",
     "BRAILLE LINE:  'Do'",
     "     VISIBLE:  'Do', cursor=3",
     "BRAILLE LINE:  'Don'",
     "     VISIBLE:  'Don', cursor=4",
     "BRAILLE LINE:  'Don'",
     "     VISIBLE:  'Don', cursor=4",
     "BRAILLE LINE:  'Done'",
     "     VISIBLE:  'Done', cursor=5",
     "BRAILLE LINE:  'Done'",
     "     VISIBLE:  'Done', cursor=5",
     "BRAILLE LINE:  'Done.'",
     "     VISIBLE:  'Done.', cursor=6",
     "BRAILLE LINE:  'Done.'",
     "     VISIBLE:  'Done.', cursor=6",
     "SPEECH OUTPUT: 'D'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Return",
    ["KNOWN ISSUE: We're not speaking anything here",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up",
    ["BRAILLE LINE:  'Done.'",
     "     VISIBLE:  'Done.', cursor=1",
     "SPEECH OUTPUT: 'Done.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up",
    ["BRAILLE LINE:  'So is this.'",
     "     VISIBLE:  'So is this.', cursor=1",
     "SPEECH OUTPUT: 'So is this.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up",
    ["KNOWN ISSUE: Something is converting the space to a Tab. The Tab is really there, however.",
     "BRAILLE LINE:  'This is	a test.'",
     "     VISIBLE:  'This is	a test.', cursor=1",
     "SPEECH OUTPUT: 'This is	a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Up",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down",
    ["BRAILLE LINE:  'So is this.'",
     "     VISIBLE:  'So is this.', cursor=1",
     "SPEECH OUTPUT: 'So is this.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down",
    ["BRAILLE LINE:  'Done.'",
     "     VISIBLE:  'Done.', cursor=1",
     "SPEECH OUTPUT: 'Done.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Up",
    ["BRAILLE LINE:  'Done.'",
     "     VISIBLE:  'Done.', cursor=1",
     "SPEECH OUTPUT: 'Done.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Up",
    ["BRAILLE LINE:  'So is this.'",
     "     VISIBLE:  'So is this.', cursor=1",
     "SPEECH OUTPUT: 'So is this.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Up",
    ["BRAILLE LINE:  'This is	a test.'",
     "     VISIBLE:  'This is	a test.', cursor=1",
     "SPEECH OUTPUT: 'This is	a test.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
