#!/usr/bin/python

"""Test of toggle button output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Expander"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line",
    ["BRAILLE LINE:  '& y Details: $l'",
     "     VISIBLE:  '& y Details: $l', cursor=1",
     "SPEECH OUTPUT: 'not pressed Details:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "2. Review previous line",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=1",
     "SPEECH OUTPUT: 'Here are some more details but not the full story.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "3. Review previous line",
    ["BRAILLE LINE:  'Something went wrong $l'",
     "     VISIBLE:  'Something went wrong $l', cursor=1",
     "SPEECH OUTPUT: 'Something went wrong'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=1",
     "SPEECH OUTPUT: 'Here are some more details but not the full story.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "5. Review next line",
    ["BRAILLE LINE:  '& y Details: $l'",
     "     VISIBLE:  '& y Details: $l', cursor=1",
     "SPEECH OUTPUT: 'not pressed Details:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  'Close $l'",
     "     VISIBLE:  'Close $l', cursor=1",
     "SPEECH OUTPUT: 'Close'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "7. Review previous line",
    ["BRAILLE LINE:  '& y Details: $l'",
     "     VISIBLE:  '& y Details: $l', cursor=1",
     "SPEECH OUTPUT: 'not pressed Details:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "8. Review previous line",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=1",
     "SPEECH OUTPUT: 'Here are some more details but not the full story.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=6",
     "SPEECH OUTPUT: 'are '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=10",
     "SPEECH OUTPUT: 'some '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=15",
     "SPEECH OUTPUT: 'more '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=20",
     "SPEECH OUTPUT: 'details '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "13. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=28",
     "SPEECH OUTPUT: 'but '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "14. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'not the full story. $l', cursor=1",
     "SPEECH OUTPUT: 'not '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "15. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'not the full story. $l', cursor=5",
     "SPEECH OUTPUT: 'the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "16. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'not the full story. $l', cursor=9",
     "SPEECH OUTPUT: 'full '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "17. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'not the full story. $l', cursor=14",
     "SPEECH OUTPUT: 'story.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "18. Tab to change focus",
    ["KNOWN ISSUE: This is not on screen. But we don't control focus.",
     "BRAILLE LINE:  'the window. Do it already ! $l rdonly'",
     "     VISIBLE:  'the window. Do it already ! $l r', cursor=28",
     "BRAILLE LINE:  'the window. Do it already ! $l rdonly'",
     "     VISIBLE:  'the window. Do it already ! $l r', cursor=28",
     "SPEECH OUTPUT: 'read only text.'",
     "SPEECH OUTPUT: 'the window. Do it already !'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "19. Review current line",
    ["BRAILLE LINE:  'Something went wrong $l'",
     "     VISIBLE:  'Something went wrong $l', cursor=1",
     "SPEECH OUTPUT: 'Something went wrong'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
