#!/usr/bin/python

"""Test of object navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Home'",
     "     VISIBLE:  'Home', cursor=1",
     "SPEECH OUTPUT: 'Home link.' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  'Bugzilla'",
     "     VISIBLE:  'Bugzilla', cursor=1",
     "SPEECH OUTPUT: 'Bugzilla'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'New bug'",
     "     VISIBLE:  'New bug', cursor=1",
     "SPEECH OUTPUT: 'New bug link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. line Down",
    ["BRAILLE LINE:  'Browse'",
     "     VISIBLE:  'Browse', cursor=1",
     "SPEECH OUTPUT: 'Browse link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. line Down",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BRAILLE LINE:  'Search'",
     "     VISIBLE:  'Search', cursor=1",
     "SPEECH OUTPUT: 'Search link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  'Reports'",
     "     VISIBLE:  'Reports', cursor=1",
     "SPEECH OUTPUT: 'Reports link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  'Account'",
     "     VISIBLE:  'Account', cursor=1",
     "SPEECH OUTPUT: 'Account link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. line Down",
    ["BRAILLE LINE:  'Admin'",
     "     VISIBLE:  'Admin', cursor=1",
     "SPEECH OUTPUT: 'Admin link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. line Down",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. line Down",
    ["BRAILLE LINE:  'Help'",
     "     VISIBLE:  'Help', cursor=1",
     "SPEECH OUTPUT: 'Help link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. line Up",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. line Up",
    ["BRAILLE LINE:  'Admin'",
     "     VISIBLE:  'Admin', cursor=1",
     "SPEECH OUTPUT: 'Admin link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. line Up",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. line Up",
    ["BRAILLE LINE:  'Account'",
     "     VISIBLE:  'Account', cursor=1",
     "SPEECH OUTPUT: 'Account link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. line Up",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. line Up",
    ["BRAILLE LINE:  'Reports'",
     "     VISIBLE:  'Reports', cursor=1",
     "SPEECH OUTPUT: 'Reports link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. line Up",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. line Up",
    ["BRAILLE LINE:  'Search'",
     "     VISIBLE:  'Search', cursor=1",
     "SPEECH OUTPUT: 'Search link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. line Up",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. line Up",
    ["BRAILLE LINE:  'Browse'",
     "     VISIBLE:  'Browse', cursor=1",
     "SPEECH OUTPUT: 'Browse link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. line Up",
    ["BRAILLE LINE:  ' ·'",
     "     VISIBLE:  ' ·', cursor=1",
     "SPEECH OUTPUT: '·'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. line Up",
    ["BRAILLE LINE:  'New bug'",
     "     VISIBLE:  'New bug', cursor=1",
     "SPEECH OUTPUT: 'New bug link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. line Up",
    ["BRAILLE LINE:  'Bugzilla'",
     "     VISIBLE:  'Bugzilla', cursor=1",
     "SPEECH OUTPUT: 'Bugzilla'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. line Up",
    ["BRAILLE LINE:  'Home'",
     "     VISIBLE:  'Home', cursor=1",
     "SPEECH OUTPUT: 'Home link.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
