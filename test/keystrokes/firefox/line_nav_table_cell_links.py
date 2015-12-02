#!/usr/bin/python

"""Test of line navigation with links in a cell with line breaks."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Here are some links'",
     "     VISIBLE:  'Here are some links', cursor=1",
     "SPEECH OUTPUT: 'Here are some links'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'HTML Tags'",
     "     VISIBLE:  'HTML Tags', cursor=1",
     "SPEECH OUTPUT: 'HTML Tags.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  '<!-->'",
     "     VISIBLE:  '<!-->', cursor=1",
     "SPEECH OUTPUT: '<!-->'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '<!DOCTYPE>'",
     "     VISIBLE:  '<!DOCTYPE>', cursor=1",
     "SPEECH OUTPUT: '<!DOCTYPE>'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  '<a>'",
     "     VISIBLE:  '<a>', cursor=1",
     "SPEECH OUTPUT: '<a>'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  '<abbr>'",
     "     VISIBLE:  '<abbr>', cursor=1",
     "SPEECH OUTPUT: '<abbr>'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  '<acronym>'",
     "     VISIBLE:  '<acronym>', cursor=1",
     "SPEECH OUTPUT: '<acronym>'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  '<abbr>'",
     "     VISIBLE:  '<abbr>', cursor=1",
     "SPEECH OUTPUT: '<abbr>'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  '<a>'",
     "     VISIBLE:  '<a>', cursor=1",
     "SPEECH OUTPUT: '<a>'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  '<!DOCTYPE>'",
     "     VISIBLE:  '<!DOCTYPE>', cursor=1",
     "SPEECH OUTPUT: '<!DOCTYPE>'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  '<!-->'",
     "     VISIBLE:  '<!-->', cursor=1",
     "SPEECH OUTPUT: '<!-->'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'HTML Tags'",
     "     VISIBLE:  'HTML Tags', cursor=1",
     "SPEECH OUTPUT: 'HTML Tags.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'Here are some links'",
     "     VISIBLE:  'Here are some links', cursor=1",
     "SPEECH OUTPUT: 'Here are some links'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
