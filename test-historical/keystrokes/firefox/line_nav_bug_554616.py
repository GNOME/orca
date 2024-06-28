#!/usr/bin/python

"""Test of line navigation output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of File",
    ["BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "SPEECH OUTPUT: 'Snapshot version column header'",
     "SPEECH OUTPUT: 'Date (UTC) column header'",
     "SPEECH OUTPUT: 'Download column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008', cursor=1",
     "SPEECH OUTPUT: 'r2477.'",
     "SPEECH OUTPUT: 'Wed Nov 5 16:39:00 2008.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'installer (10190 KB)'",
     "     VISIBLE:  'installer (10190 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(10190 KB).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'portable archive (9154 KB)'",
     "     VISIBLE:  'portable archive (9154 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(9154 KB).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008'",
     "     VISIBLE:  'r2468 Tue Nov 4 16:39:02 2008', cursor=1",
     "SPEECH OUTPUT: 'r2468.'",
     "SPEECH OUTPUT: 'Tue Nov 4 16:39:02 2008.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'installer (10193 KB)'",
     "     VISIBLE:  'installer (10193 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(10193 KB).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'portable archive (9149 KB)'",
     "     VISIBLE:  'portable archive (9149 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(9149 KB).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'installer (10193 KB)'",
     "     VISIBLE:  'installer (10193 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(10193 KB).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008'",
     "     VISIBLE:  'r2468 Tue Nov 4 16:39:02 2008', cursor=1",
     "SPEECH OUTPUT: 'r2468.'",
     "SPEECH OUTPUT: 'Tue Nov 4 16:39:02 2008.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'portable archive (9154 KB)'",
     "     VISIBLE:  'portable archive (9154 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(9154 KB).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'installer (10190 KB)'",
     "     VISIBLE:  'installer (10190 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '(10190 KB).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008', cursor=1",
     "SPEECH OUTPUT: 'r2477.'",
     "SPEECH OUTPUT: 'Wed Nov 5 16:39:00 2008.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "SPEECH OUTPUT: 'Snapshot version column header'",
     "SPEECH OUTPUT: 'Date (UTC) column header'",
     "SPEECH OUTPUT: 'Download column header'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
