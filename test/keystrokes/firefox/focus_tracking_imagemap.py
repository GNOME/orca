#!/usr/bin/python

"""Test of Orca output when tabbing on a page with imagemaps."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab",
    ["KNOWN ISSUE: This seems a bit redundant/chatty",
     "BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'Test: z y x w v u t s r q p o n ', cursor=0",
     "SPEECH OUTPUT: 'z'",
     "SPEECH OUTPUT: 'link' voice=hyperlink",
     "SPEECH OUTPUT: 'z image map link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'Test: z y x w v u t s r q p o n ', cursor=0",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'link' voice=hyperlink",
     "SPEECH OUTPUT: 'y image map link'"]))

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
     "SPEECH OUTPUT: 'link' voice=hyperlink",
     "SPEECH OUTPUT: 'a image map link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["KNOWN ISSUE: Braille is displaying embedded object characters. This should be fixed as part of the braille redo.",
     "BRAILLE LINE:  'table cell \ufffc'",
     "     VISIBLE:  'table cell \ufffc', cursor=12",
     "SPEECH OUTPUT: 'wk09_frozenmovie link image' voice=hyperlink"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
