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
     "     VISIBLE:  'z y x w v u t s r q p o n m l k ', cursor=1",
     "BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'z y x w v u t s r q p o n m l k ', cursor=1",
     "SPEECH OUTPUT: 'z'",
     "SPEECH OUTPUT: 'link' voice=hyperlink",
     "SPEECH OUTPUT: 'z image map link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'y x w v u t s r q p o n m l k j ', cursor=1",
     "BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'y x w v u t s r q p o n m l k j ', cursor=1",
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
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'a', cursor=1",
     "BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'a', cursor=1",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'link' voice=hyperlink",
     "SPEECH OUTPUT: 'a image map link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  'table cell wk09_frozenmovie image'",
     "     VISIBLE:  'table cell wk09_frozenmovie imag', cursor=0",
     "BRAILLE LINE:  'table cell wk09_frozenmovie image'",
     "     VISIBLE:  'table cell wk09_frozenmovie imag', cursor=0",
     "SPEECH OUTPUT: 'wk09_frozenmovie link image' voice=hyperlink"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
