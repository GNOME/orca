#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

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
    ["BRAILLE LINE:  'gnome-clocks application Clocks frame Pause push button'",
     "     VISIBLE:  'Pause push button', cursor=1",
     "BRAILLE LINE:  'gnome-clocks application Clocks frame Pause push button'",
     "     VISIBLE:  'Pause push button', cursor=1",
     "SPEECH OUTPUT: 'Clocks frame'",
     "SPEECH OUTPUT: 'Pause push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "3. Review current line",
    ["BRAILLE LINE:  'Pause Reset $l'",
     "     VISIBLE:  'Pause Reset $l', cursor=1",
     "SPEECH OUTPUT: 'Pause Reset'"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "4. Review previous line",
    ["BRAILLE LINE:  '00 ∶ 04 ∶ 5[0-9] \\$l'",
     "     VISIBLE:  '00 ∶ 04 ∶ 5[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00 ∶ 04 ∶ 5[0-9]'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous line",
    ["BRAILLE LINE:  '& y World & y Alarm & y Stopwatch &=y Timer $l'",
     "     VISIBLE:  '& y World & y Alarm & y Stopwatc', cursor=1",
     "SPEECH OUTPUT: 'not selected World not selected Alarm not selected Stopwatch selected Timer'"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  '00 ∶ 04 ∶ 4[0-9] \\$l'",
     "     VISIBLE:  '00 ∶ 04 ∶ 4[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00 ∶ 04 ∶ 4[0-9]'"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "7. Review current line",
    ["BRAILLE LINE:  '00 ∶ 04 ∶ 3[0-9] \\$l'",
     "     VISIBLE:  '00 ∶ 04 ∶ 3[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00 ∶ 04 ∶ 3[0-9]'"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "8. Review current line",
    ["BRAILLE LINE:  '00 ∶ 04 ∶ 2[0-9] \\$l'",
     "     VISIBLE:  '00 ∶ 04 ∶ 2[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00 ∶ 04 ∶ 2[0-9]'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
