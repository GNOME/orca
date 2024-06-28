#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'Focus me 1'",
     "     VISIBLE:  'Focus me 1', cursor=1",
     "SPEECH OUTPUT: 'Focus me 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Focus me 2'",
     "     VISIBLE:  'Focus me 2', cursor=1",
     "SPEECH OUTPUT: 'Focus me 2 kill switch'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Focus me 3 push button'",
     "     VISIBLE:  'Focus me 3 push button', cursor=1",
     "SPEECH OUTPUT: 'Focus me 3 push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Focus me 4 kill switch'",
     "     VISIBLE:  'Focus me 4 kill switch', cursor=1",
     "SPEECH OUTPUT: 'Focus me 4 kill switch'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Focus me 5 push button Focus me 6 kill switch'",
     "     VISIBLE:  'Focus me 5 push button Focus me ', cursor=1",
     "SPEECH OUTPUT: 'Focus me 5 push button'",
     "SPEECH OUTPUT: 'Focus me 6 kill switch'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Here are some slides'",
     "     VISIBLE:  'Here are some slides', cursor=1",
     "SPEECH OUTPUT: 'Presentation slide set'",
     "SPEECH OUTPUT: 'Here are some slides'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
