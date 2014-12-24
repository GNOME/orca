#!/usr/bin/python

"""Test of presentation of Dojo's panel text."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "1. Space to press the Show TabContainer Dialog",
    ["BRAILLE LINE:  'TabContainer Dialog dialog'",
     "     VISIBLE:  'TabContainer Dialog dialog', cursor=1",
     "BRAILLE LINE:  'First tab page tab Second tab page tab'",
     "     VISIBLE:  'First tab page tab Second tab pa', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'First tab page tab'",
     "     VISIBLE:  'First tab page tab', cursor=1",
     "SPEECH OUTPUT: 'TabContainer Dialog First tab Second tab This is the first tab. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut ligula. Proin porta rutrum lacus. Etiam consequat scelerisque quam. Nulla facilisi. Maecenas luctus venenatis nulla. In sit amet dui non mi semper iaculis. Sed molestie tortor at ipsum. Morbi dictum rutrum magna. Sed vitae risus. '",
     "SPEECH OUTPUT: 'First tab page tab'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right Arrow to the Second tab page",
    ["BRAILLE LINE:  'Second tab page tab'",
     "     VISIBLE:  'Second tab page tab', cursor=1",
     "BRAILLE LINE:  'Second tab page tab'",
     "     VISIBLE:  'Second tab page tab', cursor=1",
     "SPEECH OUTPUT: 'Second tab page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab into the panel",
    ["BRAILLE LINE:  'ipsum dolor sit amet'",
     "     VISIBLE:  'ipsum dolor sit amet', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "BRAILLE LINE:  'Make it overflow. ipsum dolor sit amet, consectetuer adipiscing'",
     "     VISIBLE:  'ipsum dolor sit amet, consectetu', cursor=1",
     "SPEECH OUTPUT: 'ipsum dolor sit amet link'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow in Browse Mode",
    ["BRAILLE LINE:  'elit. Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut'",
     "     VISIBLE:  'elit. Aenean semper sagittis vel', cursor=1",
     "SPEECH OUTPUT: 'elit. Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow in Browse Mode",
    ["BRAILLE LINE:  'ligula. Proin porta rutrum lacus. Etiam consequat scelerisque'",
     "     VISIBLE:  'ligula. Proin porta rutrum lacus', cursor=1",
     "SPEECH OUTPUT: 'ligula. Proin porta rutrum lacus. Etiam consequat scelerisque'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
