#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Shift Tab",
    ["BRAILLE LINE:  'document web'",
     "     VISIBLE:  'document web', cursor=1",
     "SPEECH OUTPUT: 'document web'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo link.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
