#!/usr/bin/python

"""Test of table cell structural navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("t"))
sequence.append(utils.AssertPresentationAction(
    "1. t",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'table with 4 rows 3 columns'",
     "     VISIBLE:  'table with 4 rows 3 columns', cursor=0",
     "BRAILLE LINE:  'Snapshot version'",
     "     VISIBLE:  'Snapshot version', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'table with 4 rows 3 columns' voice=system",
     "SPEECH OUTPUT: 'Snapshot version'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Alt Shift Down",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008', cursor=1",
     "BRAILLE LINE:  'r2477'",
     "     VISIBLE:  'r2477', cursor=1",
     "BRAILLE LINE:  'Row 2, column 1.'",
     "     VISIBLE:  'Row 2, column 1.', cursor=0",
     "SPEECH OUTPUT: 'r2477.'",
     "SPEECH OUTPUT: 'Row 2, column 1.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Alt Shift Right",
    ["BRAILLE LINE:  'r2477'",
     "     VISIBLE:  'r2477', cursor=1",
     "BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008', cursor=7",
     "BRAILLE LINE:  'Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008', cursor=1",
     "BRAILLE LINE:  'Row 2, column 2.'",
     "     VISIBLE:  'Row 2, column 2.', cursor=0",
     "SPEECH OUTPUT: 'Date (UTC)'",
     "SPEECH OUTPUT: 'Wed Nov 5 16:39:00 2008.'",
     "SPEECH OUTPUT: 'Row 2, column 2.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Alt Shift Right",
    ["KNOWN ISSUE: Excessive amount of updating here and in other assertions.",
     "BRAILLE LINE:  'Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008', cursor=1",
     "BRAILLE LINE:  'installer (10190 KB)'",
     "     VISIBLE:  'installer (10190 KB)', cursor=1",
     "BRAILLE LINE:  'installer (10190 KB) portable archive (9154 KB)'",
     "     VISIBLE:  'installer (10190 KB) portable ar', cursor=1",
     "BRAILLE LINE:  'Row 2, column 3.'",
     "     VISIBLE:  'Row 2, column 3.', cursor=0",
     "SPEECH OUTPUT: 'Download'",
     "SPEECH OUTPUT: 'installer'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Download column header (10190 KB)'",
     "SPEECH OUTPUT: 'portable archive'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Download column header (9154 KB)'",
     "SPEECH OUTPUT: 'Row 2, column 3.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Alt Shift Down",
    ["BRAILLE LINE:  'installer (10190 KB) portable archive (9154 KB)'",
     "     VISIBLE:  'installer (10190 KB) portable ar', cursor=1",
     "BRAILLE LINE:  'installer (10193 KB)'",
     "     VISIBLE:  'installer (10193 KB)', cursor=1",
     "BRAILLE LINE:  'installer (10193 KB) portable archive (9149 KB)'",
     "     VISIBLE:  'installer (10193 KB) portable ar', cursor=1",
     "BRAILLE LINE:  'Row 3, column 3.'",
     "     VISIBLE:  'Row 3, column 3.', cursor=0",
     "SPEECH OUTPUT: 'installer'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Download column header (10193 KB)'",
     "SPEECH OUTPUT: 'portable archive'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Download column header (9149 KB)'",
     "SPEECH OUTPUT: 'Row 3, column 3.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Alt Shift Left",
    ["BRAILLE LINE:  'installer (10193 KB) portable archive (9149 KB)'",
     "     VISIBLE:  'installer (10193 KB) portable ar', cursor=1",
     "BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008'",
     "     VISIBLE:  'r2468 Tue Nov 4 16:39:02 2008', cursor=7",
     "BRAILLE LINE:  'Tue Nov 4 16:39:02 2008'",
     "     VISIBLE:  'Tue Nov 4 16:39:02 2008', cursor=1",
     "BRAILLE LINE:  'Row 3, column 2.'",
     "     VISIBLE:  'Row 3, column 2.', cursor=0",
     "SPEECH OUTPUT: 'Date (UTC)'",
     "SPEECH OUTPUT: 'Tue Nov 4 16:39:02 2008.'",
     "SPEECH OUTPUT: 'Row 3, column 2.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Alt Shift Up",
    ["BRAILLE LINE:  'Tue Nov 4 16:39:02 2008'",
     "     VISIBLE:  'Tue Nov 4 16:39:02 2008', cursor=1",
     "BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008', cursor=7",
     "BRAILLE LINE:  'Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008', cursor=1",
     "BRAILLE LINE:  'Row 2, column 2.'",
     "     VISIBLE:  'Row 2, column 2.', cursor=0",
     "SPEECH OUTPUT: 'Wed Nov 5 16:39:00 2008.'",
     "SPEECH OUTPUT: 'Row 2, column 2.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>End"))
sequence.append(utils.AssertPresentationAction(
    "8. Alt Shift End",
    ["BRAILLE LINE:  'Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008', cursor=1",
     "BRAILLE LINE:  'installer (10186 KB)'",
     "     VISIBLE:  'installer (10186 KB)', cursor=1",
     "BRAILLE LINE:  'installer (10186 KB) portable archive (9146 KB)'",
     "     VISIBLE:  'installer (10186 KB) portable ar', cursor=1",
     "BRAILLE LINE:  'Row 4, column 3.'",
     "     VISIBLE:  'Row 4, column 3.', cursor=0",
     "SPEECH OUTPUT: 'Download'",
     "SPEECH OUTPUT: 'installer'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Download column header (10186 KB)'",
     "SPEECH OUTPUT: 'portable archive'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Download column header (9146 KB)'",
     "SPEECH OUTPUT: 'Row 4, column 3.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Home"))
sequence.append(utils.AssertPresentationAction(
    "9. Alt Shift Home",
    ["BRAILLE LINE:  'installer (10186 KB) portable archive (9146 KB)'",
     "     VISIBLE:  'installer (10186 KB) portable ar', cursor=1",
     "BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "BRAILLE LINE:  'Snapshot version'",
     "     VISIBLE:  'Snapshot version', cursor=1",
     "BRAILLE LINE:  'Row 1, column 1.'",
     "     VISIBLE:  'Row 1, column 1.', cursor=0",
     "SPEECH OUTPUT: 'Snapshot version column header'",
     "SPEECH OUTPUT: 'Row 1, column 1.' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
