# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of table cell navigation output of Firefox. 
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-554616.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "SPEECH OUTPUT: 'Snapshot version column header Date (UTC) column header Download column header'"]))

########################################################################
# T to move to the table.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("t"))
sequence.append(utils.AssertPresentationAction(
    "2. t",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'Table with 4 rows 3 columns'",
     "SPEECH OUTPUT: 'Snapshot version column header'"]))

########################################################################
# Alt+Shift+Arrow to move amongst cells
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Alt Shift Down",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008 in', cursor=1",
     "BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008 in', cursor=1",
     "SPEECH OUTPUT: 'r2477'",
     "SPEECH OUTPUT: 'Row 2, column 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Alt Shift Right",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008 installe', cursor=1",
     "BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008 installe', cursor=1",
     "SPEECH OUTPUT: 'Date (UTC)'",
     "SPEECH OUTPUT: 'Wed Nov 5 16:39:00 2008'",
     "SPEECH OUTPUT: 'Row 2, column 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Alt Shift Right",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'installer (10190 KB)portable arc', cursor=1",
     "BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'installer (10190 KB)portable arc', cursor=1",
     "SPEECH OUTPUT: 'Download'",
     "SPEECH OUTPUT: 'installer link  (10190 KB)",
     " portable archive link  (9154 KB)'",
     "SPEECH OUTPUT: 'Row 2, column 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Alt Shift Down",
    ["BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008 installer (10193 KB)'",
     "     VISIBLE:  'installer (10193 KB)', cursor=1",
     "BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008 installer (10193 KB)'",
     "     VISIBLE:  'installer (10193 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer link  (10193 KB)",
     " portable archive link  (9149 KB)'",
     "SPEECH OUTPUT: 'Row 3, column 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Alt Shift Left",
    ["BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008 installer (10193 KB)'",
     "     VISIBLE:  'Tue Nov 4 16:39:02 2008 installe', cursor=1",
     "BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008 installer (10193 KB)'",
     "     VISIBLE:  'Tue Nov 4 16:39:02 2008 installe', cursor=1",
     "SPEECH OUTPUT: 'Date (UTC)'",
     "SPEECH OUTPUT: 'Tue Nov 4 16:39:02 2008'",
     "SPEECH OUTPUT: 'Row 3, column 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Alt Shift Up",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008 installe', cursor=1",
     "BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008 installer (10190 KB)portable archive (9154 KB)'",
     "     VISIBLE:  'Wed Nov 5 16:39:00 2008 installe', cursor=1",
     "SPEECH OUTPUT: 'Wed Nov 5 16:39:00 2008'",
     "SPEECH OUTPUT: 'Row 2, column 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>End"))
sequence.append(utils.AssertPresentationAction(
    "9. Alt Shift End",
    ["BRAILLE LINE:  'r2464 Mon Nov 3 16:39:48 2008 installer (10186 KB)'",
     "     VISIBLE:  'installer (10186 KB)', cursor=1",
     "BRAILLE LINE:  'r2464 Mon Nov 3 16:39:48 2008 installer (10186 KB)'",
     "     VISIBLE:  'installer (10186 KB)', cursor=1",
     "SPEECH OUTPUT: 'Download'",
     "SPEECH OUTPUT: 'installer link  (10186 KB)",
     " portable archive link  (9146 KB)'",
     "SPEECH OUTPUT: 'Row 4, column 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Home"))
sequence.append(utils.AssertPresentationAction(
    "10. Alt Shift Home",
    ["BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "SPEECH OUTPUT: 'Snapshot version column header'",
     "SPEECH OUTPUT: 'Row 1, column 1.'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
