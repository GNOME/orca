#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("nano"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("So is this."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Done."))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "2. Review previous line",
    ["BRAILLE LINE:  'Done. $l'",
     "     VISIBLE:  'Done. $l', cursor=1",
     "SPEECH OUTPUT: 'Done.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "3. Review previous line",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=1",
     "SPEECH OUTPUT: 'So is this.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "4. Review previous line",
    ["KNOWN ISSUE: Something is converting the space to a Tab. The Tab is really there, however.",
     "BRAILLE LINE:  'This is	a test. $l'",
     "     VISIBLE:  'This is	a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is	a test.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  'This is	a test. $l'",
     "     VISIBLE:  'This is	a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is	a test.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=1",
     "SPEECH OUTPUT: 'So is this.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next line",
    ["BRAILLE LINE:  'Done. $l'",
     "     VISIBLE:  'Done. $l', cursor=1",
     "SPEECH OUTPUT: 'Done.",
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
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyComboAction("KP_9"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next line",
    ["BRAILLE LINE:  '^G Get Help  ^O Write Out ^W Where Is  ^K Cut Text  ^J Justify   ^C Cur Pos $l'",
     "     VISIBLE:  '^G Get Help  ^O Write Out ^W Whe', cursor=1",
     "SPEECH OUTPUT: '^G Get Help  ^O Write Out ^W Where Is  ^K Cut Text  ^J Justify   ^C Cur Pos",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next line",
    ["BRAILLE LINE:  '^X Exit      ^R Read File ^\\ Replace   ^U Uncut Text^T To Spell  ^_ Go To Line $l'",
     "     VISIBLE:  '^X Exit      ^R Read File ^\\ Rep', cursor=1",
     "SPEECH OUTPUT: '^X Exit      ^R Read File ^\\ Replace   ^U Uncut Text^T To Spell  ^_ Go To Line",
     "'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
