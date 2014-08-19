#!/usr/bin/python

"""Test of navigation given a paragraph with a multi-line-high initial char."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This is a normal paragraph.'",
     "     VISIBLE:  'This is a normal paragraph.', cursor=1",
     "SPEECH OUTPUT: 'This is a normal paragraph.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  'So is this one, but the next one will not be.'",
     "     VISIBLE:  'So is this one, but the next one', cursor=1",
     "SPEECH OUTPUT: 'So is this one, but the next one will not be.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down",
    ["BRAILLE LINE:  'W'",
     "     VISIBLE:  'W', cursor=1",
     "SPEECH OUTPUT: 'W'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down",
    ["BRAILLE LINE:  'W   hy did the chicken cross the road? Give up? It was to escape from the enormous capital letter at the'",
     "     VISIBLE:  '   hy did the chicken cross the ', cursor=1",
     "SPEECH OUTPUT: 'W'",
     "SPEECH OUTPUT: '   hy did the chicken cross the road? Give up? It was to escape from the enormous capital letter at the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down",
    ["BRAILLE LINE:  'beginning of this paragraph. These are the things that keep chickens up at night. No. Really.They are.'",
     "     VISIBLE:  'beginning of this paragraph. The', cursor=1",
     "SPEECH OUTPUT: 'beginning of this paragraph. These are the things that keep chickens up at night. No. Really.They are. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down",
    ["BRAILLE LINE:  'Here's another normal paragraph.'",
     "     VISIBLE:  'Here's another normal paragraph.', cursor=1",
     "SPEECH OUTPUT: 'Here's another normal paragraph.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "7. End of file", 
    ["BRAILLE LINE:  'Here's another normal paragraph.'",
     "     VISIBLE:  'Here's another normal paragraph.', cursor=32",
     "SPEECH OUTPUT: 'Here's another normal paragraph.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Up",
    ["BRAILLE LINE:  'beginning of this paragraph. These are the things that keep chickens up at night. No. Really.They are.'",
     "     VISIBLE:  'beginning of this paragraph. The', cursor=1",
     "SPEECH OUTPUT: 'beginning of this paragraph. These are the things that keep chickens up at night. No. Really.They are. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Up",
    ["KNOWN ISSUE: We are not combining the W with the non-huge text that follows",
     "BRAILLE LINE:  'W'",
     "     VISIBLE:  'W', cursor=1",
     "SPEECH OUTPUT: 'W'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Up",
    ["BRAILLE LINE:  'So is this one, but the next one will not be.'",
     "     VISIBLE:  'So is this one, but the next one', cursor=1",
     "SPEECH OUTPUT: 'So is this one, but the next one will not be.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Up",
    ["BRAILLE LINE:  'This is a normal paragraph.'",
     "     VISIBLE:  'This is a normal paragraph.', cursor=1",
     "SPEECH OUTPUT: 'This is a normal paragraph.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
