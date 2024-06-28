#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to next radio button",
    ["BRAILLE LINE:  '& y yes radio button'",
     "     VISIBLE:  '& y yes radio button', cursor=1",
     "SPEECH OUTPUT: 'yes.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to next radio button",
    ["BRAILLE LINE:  '& y well, maybe... radio button'",
     "     VISIBLE:  '& y well, maybe... radio button', cursor=1",
     "SPEECH OUTPUT: 'well, maybe...'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to next radio button",
    ["BRAILLE LINE:  '& y Yes radio button'",
     "     VISIBLE:  '& y Yes radio button', cursor=1",
     "SPEECH OUTPUT: 'Yes.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
