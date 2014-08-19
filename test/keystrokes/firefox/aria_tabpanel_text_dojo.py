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
    ["BRAILLE LINE:  'TabContainer Dialog h0  Cancel push button'",
     "     VISIBLE:  'TabContainer Dialog h0  Cancel p', cursor=0",
     "BRAILLE LINE:  'First tab'",
     "     VISIBLE:  'First tab', cursor=1",
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
     "BRAILLE LINE:  'ipsum dolor sit amet'",
     "     VISIBLE:  'ipsum dolor sit amet', cursor=1",
     "SPEECH OUTPUT: 'ipsum dolor sit amet'",
     "SPEECH OUTPUT: 'link' voice=hyperlink",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow in Browse Mode",
    ["KNOWN ISSUE: We're winding up at the end of the line rather than on the next line",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow in Browse Mode",
    ["BRAILLE LINE:  'lacus. Etiam consequat scelerisque quam. Nulla facilisi. Maecenas luctus'",
     "     VISIBLE:  'lacus. Etiam consequat scelerisq', cursor=1",
     "SPEECH OUTPUT: 'lacus. Etiam consequat scelerisque quam. Nulla facilisi. Maecenas luctus '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
