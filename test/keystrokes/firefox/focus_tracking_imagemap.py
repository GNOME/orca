#!/usr/bin/python

"""Test of Orca output when tabbing on a page with imagemaps."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'Test: z y x w v u t s r q p o n ', cursor=0",
     "SPEECH OUTPUT: 'z'",
     "SPEECH OUTPUT: 'image map link rect' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'Test: z y x w v u t s r q p o n ', cursor=0",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'image map link rect' voice=hyperlink"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["KNOWN ISSUE: Braille is not displaying the focused link. This should be fixed as part of the braille redo.",
     "BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'Test: z y x w v u t s r q p o n ', cursor=0",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'image map link rect' voice=hyperlink"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  'wk09_frozenmovie'",
     "     VISIBLE:  'wk09_frozenmovie', cursor=1",
     "SPEECH OUTPUT: 'wk09_frozenmovie link image' voice=hyperlink"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
