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
    ["BRAILLE LINE:  'Something went wrong $l'",
     "     VISIBLE:  'Something went wrong $l', cursor=1",
     "SPEECH OUTPUT: 'Something went wrong'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "2. Review previous line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "3. Review next line",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=1",
     "SPEECH OUTPUT: 'Here are some more details but not the full story.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["KNOWN ISSUE: We're skipping over the Details expander",
     "BRAILLE LINE:  'Close $l'",
     "     VISIBLE:  'Close $l', cursor=1",
     "SPEECH OUTPUT: 'Close'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "5. Review next line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "6. Review previous line",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=1",
     "SPEECH OUTPUT: 'Here are some more details but not the full story.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=6",
     "SPEECH OUTPUT: 'are '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=10",
     "SPEECH OUTPUT: 'some '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=15",
     "SPEECH OUTPUT: 'more '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=20",
     "SPEECH OUTPUT: 'details '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=28",
     "SPEECH OUTPUT: 'but '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'Here are some more details but n', cursor=32",
     "SPEECH OUTPUT: 'not '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "13. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'ot the full story. $l', cursor=4",
     "SPEECH OUTPUT: 'the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "14. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'ot the full story. $l', cursor=8",
     "SPEECH OUTPUT: 'full '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "15. Review next word",
    ["BRAILLE LINE:  'Here are some more details but not the full story. $l'",
     "     VISIBLE:  'ot the full story. $l', cursor=13",
     "SPEECH OUTPUT: 'story.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "16. Review next word",
    ["KNOWN ISSUE: We're skipping over the Details expander",
     "BRAILLE LINE:  'Close $l'",
     "     VISIBLE:  'Close $l', cursor=1",
     "SPEECH OUTPUT: 'Close'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "17. Tab to change focus",
    ["KNOWN ISSUE: This is not on screen. But we don't control focus.",
     "BRAILLE LINE:  'already ! $l rdonly'",
     "     VISIBLE:  'already ! $l rdonly', cursor=10",
     "BRAILLE LINE:  'already ! $l rdonly'",
     "     VISIBLE:  'already ! $l rdonly', cursor=10",
     "SPEECH OUTPUT: 'read only text.'",
     "SPEECH OUTPUT: 'already !'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "18. Review current line",
    ["BRAILLE LINE:  'Something went wrong $l'",
     "     VISIBLE:  'Something went wrong $l', cursor=1",
     "SPEECH OUTPUT: 'Something went wrong'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
