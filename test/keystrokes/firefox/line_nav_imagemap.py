#!/usr/bin/python

"""Test of line navigation on a page with an imagemap."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This looks like A to Z, but it's really Z to A.'",
     "     VISIBLE:  'This looks like A to Z, but it's', cursor=1",
     "SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'Test: z y x w v u t s r q p o n ', cursor=1",
     "SPEECH OUTPUT: 'Test:.'",
     "SPEECH OUTPUT: 'z image map link.'",
     "SPEECH OUTPUT: 'y image map link.'",
     "SPEECH OUTPUT: 'x image map link.'",
     "SPEECH OUTPUT: 'w image map link.'",
     "SPEECH OUTPUT: 'v image map link.'",
     "SPEECH OUTPUT: 'u image map link.'",
     "SPEECH OUTPUT: 't image map link.'",
     "SPEECH OUTPUT: 's image map link.'",
     "SPEECH OUTPUT: 'r image map link.'",
     "SPEECH OUTPUT: 'q image map link.'",
     "SPEECH OUTPUT: 'p image map link.'",
     "SPEECH OUTPUT: 'o image map link.'",
     "SPEECH OUTPUT: 'n image map link.'",
     "SPEECH OUTPUT: 'm image map link.'",
     "SPEECH OUTPUT: 'l image map link.'",
     "SPEECH OUTPUT: 'k image map link.'",
     "SPEECH OUTPUT: 'j image map link.'",
     "SPEECH OUTPUT: 'i image map link.'",
     "SPEECH OUTPUT: 'h image map link.'",
     "SPEECH OUTPUT: 'g image map link.'",
     "SPEECH OUTPUT: 'f image map link.'",
     "SPEECH OUTPUT: 'e image map link.'",
     "SPEECH OUTPUT: 'd image map link.'",
     "SPEECH OUTPUT: 'c image map link.'",
     "SPEECH OUTPUT: 'b image map link.'",
     "SPEECH OUTPUT: 'a image map link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'Here is some text.'",
     "     VISIBLE:  'Here is some text.', cursor=1",
     "SPEECH OUTPUT: 'Here is some text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. line Up",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'Test: z y x w v u t s r q p o n ', cursor=1",
     "SPEECH OUTPUT: 'Test:.'",
     "SPEECH OUTPUT: 'z image map link.'",
     "SPEECH OUTPUT: 'y image map link.'",
     "SPEECH OUTPUT: 'x image map link.'",
     "SPEECH OUTPUT: 'w image map link.'",
     "SPEECH OUTPUT: 'v image map link.'",
     "SPEECH OUTPUT: 'u image map link.'",
     "SPEECH OUTPUT: 't image map link.'",
     "SPEECH OUTPUT: 's image map link.'",
     "SPEECH OUTPUT: 'r image map link.'",
     "SPEECH OUTPUT: 'q image map link.'",
     "SPEECH OUTPUT: 'p image map link.'",
     "SPEECH OUTPUT: 'o image map link.'",
     "SPEECH OUTPUT: 'n image map link.'",
     "SPEECH OUTPUT: 'm image map link.'",
     "SPEECH OUTPUT: 'l image map link.'",
     "SPEECH OUTPUT: 'k image map link.'",
     "SPEECH OUTPUT: 'j image map link.'",
     "SPEECH OUTPUT: 'i image map link.'",
     "SPEECH OUTPUT: 'h image map link.'",
     "SPEECH OUTPUT: 'g image map link.'",
     "SPEECH OUTPUT: 'f image map link.'",
     "SPEECH OUTPUT: 'e image map link.'",
     "SPEECH OUTPUT: 'd image map link.'",
     "SPEECH OUTPUT: 'c image map link.'",
     "SPEECH OUTPUT: 'b image map link.'",
     "SPEECH OUTPUT: 'a image map link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. line Up",
    ["BRAILLE LINE:  'This looks like A to Z, but it's really Z to A.'",
     "     VISIBLE:  'This looks like A to Z, but it's', cursor=1",
     "SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
