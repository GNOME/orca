# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox. 
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
    "Top of file",
    ["BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "SPEECH OUTPUT: 'Snapshot version Date (UTC) Download'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008', cursor=1",
     "SPEECH OUTPUT: 'r2477 Wed Nov 5 16:39:00 2008"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'installer (10190 KB)'",
     "     VISIBLE:  'installer (10190 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer link  (10190 KB)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'portable archive (9154 KB)'",
     "     VISIBLE:  'portable archive (9154 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive link  (9154 KB)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008'",
     "     VISIBLE:  'r2468 Tue Nov 4 16:39:02 2008', cursor=1",
     "SPEECH OUTPUT: 'r2468 Tue Nov 4 16:39:02 2008"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'installer (10193 KB)'",
     "     VISIBLE:  'installer (10193 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer link  (10193 KB)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'portable archive (9149 KB)'",
     "     VISIBLE:  'portable archive (9149 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive link  (9149 KB)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'r2464 Mon Nov 3 16:39:48 2008'",
     "     VISIBLE:  'r2464 Mon Nov 3 16:39:48 2008', cursor=1",
     "SPEECH OUTPUT: 'r2464 Mon Nov 3 16:39:48 2008"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'installer (10186 KB)'",
     "     VISIBLE:  'installer (10186 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer link  (10186 KB)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'portable archive (9146 KB)'",
     "     VISIBLE:  'portable archive (9146 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive link  (9146 KB)'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Up",
    ["BRAILLE LINE:  'installer (10186 KB)'",
     "     VISIBLE:  'installer (10186 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer link  (10186 KB)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Up",
    ["BRAILLE LINE:  'r2464 Mon Nov 3 16:39:48 2008'",
     "     VISIBLE:  'r2464 Mon Nov 3 16:39:48 2008', cursor=1",
     "SPEECH OUTPUT: 'r2464 Mon Nov 3 16:39:48 2008"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  'portable archive (9149 KB)'",
     "     VISIBLE:  'portable archive (9149 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive link  (9149 KB)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'installer (10193 KB)'",
     "     VISIBLE:  'installer (10193 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer link  (10193 KB)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'r2468 Tue Nov 4 16:39:02 2008'",
     "     VISIBLE:  'r2468 Tue Nov 4 16:39:02 2008', cursor=1",
     "SPEECH OUTPUT: 'r2468 Tue Nov 4 16:39:02 2008"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'portable archive (9154 KB)'",
     "     VISIBLE:  'portable archive (9154 KB)', cursor=1",
     "SPEECH OUTPUT: 'portable archive link  (9154 KB)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'installer (10190 KB)'",
     "     VISIBLE:  'installer (10190 KB)', cursor=1",
     "SPEECH OUTPUT: 'installer link  (10190 KB)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'r2477 Wed Nov 5 16:39:00 2008'",
     "     VISIBLE:  'r2477 Wed Nov 5 16:39:00 2008', cursor=1",
     "SPEECH OUTPUT: 'r2477 Wed Nov 5 16:39:00 2008"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'Snapshot version Date (UTC) Download'",
     "     VISIBLE:  'Snapshot version Date (UTC) Down', cursor=1",
     "SPEECH OUTPUT: 'Snapshot version Date (UTC) Download'"]))

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
