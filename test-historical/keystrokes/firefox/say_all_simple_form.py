#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Type something here:'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'Magic disappearing text trick:'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'tab to me and I disappear'",
     "SPEECH OUTPUT: 'Tell me a secret:'",
     "SPEECH OUTPUT: 'password text'",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'I am a monkey with a long tail. '",
     "SPEECH OUTPUT: '  I like to swing from trees and eat bananas. '",
     "SPEECH OUTPUT: '  I've recently taken up typing and plan to write my memoirs.",
     "'",
     "SPEECH OUTPUT: '",
     "     '",
     "SPEECH OUTPUT: 'Check one or more:'",
     "SPEECH OUTPUT: 'Red'",
     "SPEECH OUTPUT: 'check box'",
     "SPEECH OUTPUT: 'not checked'",
     "SPEECH OUTPUT: 'Red'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'Blue'",
     "SPEECH OUTPUT: 'check box'",
     "SPEECH OUTPUT: 'not checked'",
     "SPEECH OUTPUT: 'Blue'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'Green'",
     "SPEECH OUTPUT: 'check box'",
     "SPEECH OUTPUT: 'not checked'",
     "SPEECH OUTPUT: 'Green'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'Make a selection:'",
     "SPEECH OUTPUT: 'Water'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'Which sports do you like?'",
     "SPEECH OUTPUT: 'multi-select'",
     "SPEECH OUTPUT: 'List with 4 items'",
     "SPEECH OUTPUT: 'Dashing picture of Willie Walker'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Ain't he handsome (please say yes)?'",
     "SPEECH OUTPUT: 'not selected'",
     "SPEECH OUTPUT: 'radio button'",
     "SPEECH OUTPUT: 'Yes'",
     "SPEECH OUTPUT: 'not selected'",
     "SPEECH OUTPUT: 'radio button'",
     "SPEECH OUTPUT: 'No'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
