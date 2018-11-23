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
sequence.append(KeyComboAction("a"))
sequence.append(utils.AssertPresentationAction(
    "1. a for next clickable",
    ["BRAILLE LINE:  'Hello'",
     "     VISIBLE:  'Hello', cursor=1",
     "SPEECH OUTPUT: 'Hello clickable'"]))

sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Divide"))
sequence.append(PauseAction(5000))
sequence.append(utils.AssertPresentationAction(
    "2. KP_Divide to click on clickable",
    ["BRAILLE LINE:  'Goodbye cruel'",
     "     VISIBLE:  'Goodbye cruel', cursor=1",
     "SPEECH OUTPUT: 'Goodbye cruel clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>a"))
sequence.append(PauseAction(5000))
sequence.append(utils.AssertPresentationAction(
    "3. Alt+a for Activate button",
    ["BRAILLE LINE:  'runorca.py application Clickables: 1 item found dialog'",
     "     VISIBLE:  'Clickables: 1 item found dialog', cursor=1",
     "BRAILLE LINE:  'runorca.py application Clickables: 1 item found dialog table Clickable column header Goodbye cruel static'",
     "     VISIBLE:  'Goodbye cruel static', cursor=1",
     "SPEECH OUTPUT: 'Clickables: 1 item found'",
     "SPEECH OUTPUT: 'table with 1 row 2 columns'",
     "SPEECH OUTPUT: 'Goodbye cruel.'",
     "SPEECH OUTPUT: 'static.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>a"))
sequence.append(PauseAction(5000))
sequence.append(utils.AssertPresentationAction(
    "4. Alt+a for Activate button",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame'",
     "     VISIBLE:  'Firefox Nightly frame', cursor=1",
     "BRAILLE LINE:  'Goodbye cruel'",
     "     VISIBLE:  'Goodbye cruel', cursor=1",
     "SPEECH OUTPUT: 'Firefox Nightly frame'",
     "SPEECH OUTPUT: 'Hello clickable'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
