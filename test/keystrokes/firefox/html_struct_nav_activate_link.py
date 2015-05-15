#!/usr/bin/python

"""Test for activation of a link after using structural navigation"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("3"))
sequence.append(utils.AssertPresentationAction(
    "1. Press 3 to move to the heading at level 3",
    ["BRAILLE LINE:  '1. Anchors2.html h3'",
     "     VISIBLE:  '1. Anchors2.html h3', cursor=4",
     "BRAILLE LINE:  '1. Anchors2.html h3'",
     "     VISIBLE:  '1. Anchors2.html h3', cursor=4",
     "SPEECH OUTPUT: 'Anchors2.html'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Press Return to active the link",
    ["BRAILLE LINE:  'Finished loading Links to test files.'",
     "     VISIBLE:  'Finished loading Links to test f', cursor=0",
     "BRAILLE LINE:  'Here are some of our local test files:'",
     "     VISIBLE:  'Here are some of our local test ', cursor=1",
    "SPEECH OUTPUT: 'Finished loading Links to test files.' voice=system",
    "SPEECH OUTPUT: 'Here are some of our local test files:'",
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
