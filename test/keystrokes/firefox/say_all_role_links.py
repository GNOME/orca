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
    ["SPEECH OUTPUT: 'Here are some of our local test files:'",
     "SPEECH OUTPUT: 'List with 16 items'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'anchors.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'blockquotes.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'bugzilla_top.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'combobox.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'fieldset.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'htmlpage.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'image-test.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'linebreak-test.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'lists.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'samesizearea.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'simpleform.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'simpleheader.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'slash-test.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'status-bar.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'tables.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'textattributes.html'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
