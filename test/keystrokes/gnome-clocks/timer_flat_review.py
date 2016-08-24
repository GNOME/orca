#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("F10"))
sequence.append(KeyComboAction("space"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("F10"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("space"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line",
    ["BRAILLE LINE:  'Start $l'",
     "     VISIBLE:  'Start $l', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "2. Activate timer",
    ["BRAILLE LINE:  'gnome-clocks application frame Pause push button'",
     "     VISIBLE:  'Pause push button', cursor=1",
     "BRAILLE LINE:  'gnome-clocks application frame Pause push button'",
     "     VISIBLE:  'Pause push button', cursor=1",
     "SPEECH OUTPUT: 'frame'",
     "SPEECH OUTPUT: 'Pause push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "3. Review current line",
    ["BRAILLE LINE:  'Pause Reset $l'",
     "     VISIBLE:  'Pause Reset $l', cursor=1",
     "SPEECH OUTPUT: 'Pause Reset'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "4. Review previous line",
    ["BRAILLE LINE:  'label 00 ∶ 04 ∶ 58 label $l'",
     "     VISIBLE:  'label 00 ∶ 04 ∶ 58 label $l', cursor=1",
     "SPEECH OUTPUT: 'label 00 ∶ 04 ∶ 58 label'"])) 

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous line",
    ["BRAILLE LINE:  '& y World & y Alarm & y Stopwatch &=y Timer $l'",
     "     VISIBLE:  '& y World & y Alarm & y Stopwatc', cursor=1",
     "SPEECH OUTPUT: 'not selected World not selected Alarm not selected Stopwatch selected Timer'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  'label 00 ∶ 04 ∶ 58 label $l'",
     "     VISIBLE:  'label 00 ∶ 04 ∶ 58 label $l', cursor=1",
     "SPEECH OUTPUT: 'label 00 ∶ 04 ∶ 58 label'"])) 

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(utils.AssertPresentationAction(
    "7. Toggle flat review",
    ["BRAILLE LINE:  'Leaving flat review.'",
     "     VISIBLE:  'Leaving flat review.', cursor=0",
     "BRAILLE LINE:  'gnome-clocks application frame Pause push button'",
     "     VISIBLE:  'Pause push button', cursor=1",
     "BRAILLE LINE:  'Entering flat review.'",
     "     VISIBLE:  'Entering flat review.', cursor=0",
     "BRAILLE LINE:  'Pause Reset $l'",
     "     VISIBLE:  'Pause Reset $l', cursor=1",
     "SPEECH OUTPUT: 'Leaving flat review.' voice=system",
     "SPEECH OUTPUT: 'Entering flat review.' voice=system",
     "SPEECH OUTPUT: 'Pause'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "8. Review previous line",
    ["BRAILLE LINE:  'label 00 ∶ 04 ∶ 49 label $l'",
     "     VISIBLE:  'label 00 ∶ 04 ∶ 49 label $l', cursor=1",
     "SPEECH OUTPUT: 'label 00 ∶ 04 ∶ 49 label'"])) 

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "9. Review current line",
    ["BRAILLE LINE:  'label 00 ∶ 04 ∶ 49 label $l'",
     "     VISIBLE:  'label 00 ∶ 04 ∶ 49 label $l', cursor=1",
     "SPEECH OUTPUT: 'label 00 ∶ 04 ∶ 49 label'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "10. Review current line",
    ["KNOWN ISSUE: The values are now being displayed, but are not yet being updated. Also the labels are useless.",
     "BRAILLE LINE:  'label 00 ∶ 04 ∶ 49 label $l'",
     "     VISIBLE:  'label 00 ∶ 04 ∶ 49 label $l', cursor=1",
     "SPEECH OUTPUT: 'label 00 ∶ 04 ∶ 49 label'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
