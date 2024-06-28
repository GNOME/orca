#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("F10"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("space"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line",
    ["BRAILLE LINE:  'Start Reset $l'",
     "     VISIBLE:  'Start Reset $l', cursor=1",
     "SPEECH OUTPUT: 'Start Reset'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "2. Activate stop watch",
    ["BRAILLE LINE:  'gnome-clocks application Clocks frame Stop push button'",
     "     VISIBLE:  'Stop push button', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "3. Review current line",
    ["BRAILLE LINE:  'Start Reset $l'",
     "     VISIBLE:  'Start Reset $l', cursor=1",
     "SPEECH OUTPUT: 'Start Reset'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "4. Review previous line",
    ["BRAILLE LINE:  '00‎∶04\\.[0-9] \\$l'",
     "     VISIBLE:  '00‎∶04\\.[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00‎∶04\\.[0-9]'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous line",
    ["BRAILLE LINE:  '& y World & y Alarm &=y Stopwatch & y Timer $l'",
     "     VISIBLE:  '& y World & y Alarm &=y Stopwatc', cursor=1",
     "SPEECH OUTPUT: 'not selected World not selected Alarm selected Stopwatch not selected Timer'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  '00‎∶0(8|9)\\.[0-9] \\$l'",
     "     VISIBLE:  '00‎∶0(8|9)\\.[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00‎∶0(8|9)\\.[0-9]'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(utils.AssertPresentationAction(
    "7. Toggle flat review",
    ["BRAILLE LINE:  'Leaving flat review.'",
     "     VISIBLE:  'Leaving flat review.', cursor=0",
     "BRAILLE LINE:  'gnome-clocks application Clocks frame Stop push button'",
     "     VISIBLE:  'Stop push button', cursor=1",
     "BRAILLE LINE:  'Entering flat review.'",
     "     VISIBLE:  'Entering flat review.', cursor=0",
     "BRAILLE LINE:  'Stop Lap $l'",
     "     VISIBLE:  'Stop Lap $l', cursor=1",
     "SPEECH OUTPUT: 'Leaving flat review.' voice=system",
     "SPEECH OUTPUT: 'Entering flat review.' voice=system",
     "SPEECH OUTPUT: 'Stop'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "8. Review previous line",
    ["BRAILLE LINE:  '00‎∶(13|14)\\.[0-9] \\$l'",
     "     VISIBLE:  '00‎∶(13|14)\\.[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00‎∶(13|14)\\.[0-9]'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "9. Review current line",
    ["BRAILLE LINE:  '00‎∶(19|20)\\.[0-9] \\$l'",
     "     VISIBLE:  '00‎∶(19|20)\\.[0-9] \\$l', cursor=1",
     "SPEECH OUTPUT: '00‎∶(19|20)\\.[0-9]'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
