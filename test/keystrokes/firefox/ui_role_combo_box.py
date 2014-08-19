#!/usr/bin/python

"""Test of combo box output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Alt>e"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to combobox",
    ["KNOWN ISSUE: The braille isn't right here and in the tests that follow",
     "BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "SPEECH OUTPUT: 'Startup panel'",
     "SPEECH OUTPUT: 'When Firefox starts: Show a blank page combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow in combobox",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow in combobox",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "SPEECH OUTPUT: 'Show a blank page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Alt Down Arrow to expand combobox",
    ["KNOWN ISSUE: We should present something here.",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow in expanded combobox",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup  combo boxWhen Firefox starts: When Firefox starts: Show my windows and tabs from last time'",
     "     VISIBLE:  'Show my windows and tabs from la', cursor=1",
     "SPEECH OUTPUT: 'Show my windows and tabs from last time'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up Arrow in expanded combobox",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup  combo boxWhen Firefox starts: When Firefox starts: Show a blank page'",
     "     VISIBLE:  'Show a blank page', cursor=1",
     "SPEECH OUTPUT: 'Show a blank page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "7. Return to collapse combobox",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "SPEECH OUTPUT: 'When Firefox starts: Show a blank page combo box'",
     "SPEECH OUTPUT: 'Show a blank page'",
     "SPEECH OUTPUT: 'combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("s"))
sequence.append(utils.AssertPresentationAction(
    "8. First letter navigation with s",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "SPEECH OUTPUT: 'Show my home page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("s"))
sequence.append(utils.AssertPresentationAction(
    "9. First letter navigation with s",
    ["BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "SPEECH OUTPUT: 'Show a blank page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Basic Where Am I",
    ["KNOWN ISSUE: Crazy chattines",
     "BRAILLE LINE:  'Firefox application Firefox Preferences dialog Startup When Firefox starts: When Firefox starts: combo box'",
     "     VISIBLE:  'When Firefox starts: When Firefo', cursor=22",
     "SPEECH OUTPUT: 'Firefox Preferences'",
     "SPEECH OUTPUT: 'Startup'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: 'Show a blank page'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'Show a blank page'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'Show a blank page'",
     "SPEECH OUTPUT: '1 of 2'"]))

sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
