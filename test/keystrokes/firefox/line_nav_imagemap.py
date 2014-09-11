#!/usr/bin/python

"""Test of line navigation on a page with an imagemap."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

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
     "SPEECH OUTPUT: 'Test:'",
     "SPEECH OUTPUT: 'z'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'x'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'v'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'u'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'q'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'p'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'm'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'k'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'j'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'g'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'f'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'd'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'c'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'b'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'image map link'"]))

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
     "SPEECH OUTPUT: 'Test:'",
     "SPEECH OUTPUT: 'z'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'x'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'v'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'u'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'q'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'p'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'm'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'k'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'j'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'g'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'f'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'd'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'c'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'b'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'image map link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. line Up",
    ["BRAILLE LINE:  'This looks like A to Z, but it's really Z to A.'",
     "     VISIBLE:  'This looks like A to Z, but it's', cursor=1",
     "SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
