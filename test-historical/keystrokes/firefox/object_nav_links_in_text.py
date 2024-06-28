#!/usr/bin/python

"""Test of object navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Home'",
     "     VISIBLE:  'Home', cursor=1",
     "SPEECH OUTPUT: 'Home link.' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("H"))
sequence.append(utils.AssertPresentationAction(
    "2. H for heading",
    ["BRAILLE LINE:  'Enter Bug: orca \u2013 This page lets you enter a new bug into Bugzilla. h1'",
     "     VISIBLE:  'Enter Bug: orca \u2013 This page lets', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca \u2013 This page lets you enter a new bug into Bugzilla. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'into Bugzilla. h1'",
     "     VISIBLE:  'into Bugzilla. h1', cursor=1",
     "SPEECH OUTPUT: 'into Bugzilla. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  'Before reporting a bug, please read the'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. line Down",
    ["BRAILLE LINE:  'bug writing guidelines'",
     "     VISIBLE:  'bug writing guidelines', cursor=1",
     "SPEECH OUTPUT: 'bug writing guidelines link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. line Down",
    ["BRAILLE LINE:  ', please look at the list of'",
     "     VISIBLE:  ', please look at the list of', cursor=1",
     "SPEECH OUTPUT: ', please look at the list of.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BRAILLE LINE:  'most'",
     "     VISIBLE:  'most', cursor=1",
     "SPEECH OUTPUT: 'most link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  'frequently reported bugs'",
     "     VISIBLE:  'frequently reported bugs', cursor=1",
     "SPEECH OUTPUT: 'frequently reported bugs link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  ', and please'",
     "     VISIBLE:  ', and please', cursor=1",
     "SPEECH OUTPUT: ', and please.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  'search'",
     "     VISIBLE:  'search', cursor=1",
     "SPEECH OUTPUT: 'search link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  ' or'",
     "     VISIBLE:  ' or', cursor=1",
     "SPEECH OUTPUT: 'or.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BRAILLE LINE:  'browse'",
     "     VISIBLE:  'browse', cursor=1",
     "SPEECH OUTPUT: 'browse link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. line Down",
    ["BRAILLE LINE:  ' for the bug.'",
     "     VISIBLE:  ' for the bug.', cursor=1",
     "SPEECH OUTPUT: 'for the bug.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. line Up",
    ["BRAILLE LINE:  'browse'",
     "     VISIBLE:  'browse', cursor=1",
     "SPEECH OUTPUT: 'browse link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. line Up",
    ["BRAILLE LINE:  ' or'",
     "     VISIBLE:  ' or', cursor=1",
     "SPEECH OUTPUT: 'or.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. line Up",
    ["BRAILLE LINE:  'search'",
     "     VISIBLE:  'search', cursor=1",
     "SPEECH OUTPUT: 'search link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. line Up",
    ["BRAILLE LINE:  ', and please'",
     "     VISIBLE:  ', and please', cursor=1",
     "SPEECH OUTPUT: ', and please.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. line Up",
    ["BRAILLE LINE:  'frequently reported bugs'",
     "     VISIBLE:  'frequently reported bugs', cursor=1",
     "SPEECH OUTPUT: 'frequently reported bugs link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. line Up",
    ["BRAILLE LINE:  'most'",
     "     VISIBLE:  'most', cursor=1",
     "SPEECH OUTPUT: 'most link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. line Up",
    ["BRAILLE LINE:  ', please look at the list of'",
     "     VISIBLE:  ', please look at the list of', cursor=1",
     "SPEECH OUTPUT: ', please look at the list of.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. line Up",
    ["BRAILLE LINE:  'bug writing guidelines'",
     "     VISIBLE:  'bug writing guidelines', cursor=1",
     "SPEECH OUTPUT: 'bug writing guidelines link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. line Up",
    ["BRAILLE LINE:  'Before reporting a bug, please read the'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. line Up",
    ["BRAILLE LINE:  'into Bugzilla. h1'",
     "     VISIBLE:  'into Bugzilla. h1', cursor=1",
     "SPEECH OUTPUT: 'into Bugzilla. heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. line Up",
    ["BRAILLE LINE:  'Enter Bug: orca \u2013 This page lets you enter a new bug  h1'",
     "     VISIBLE:  'Enter Bug: orca \u2013 This page lets', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca \u2013 This page lets you enter a new bug heading level 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
