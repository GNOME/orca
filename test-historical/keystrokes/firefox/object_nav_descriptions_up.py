#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>End"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Up",
    ["BRAILLE LINE:  'Grey'",
     "     VISIBLE:  'Grey', cursor=1",
     "SPEECH OUTPUT: 'Grey clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Up",
    ["BRAILLE LINE:  '< > Grey check box'",
     "     VISIBLE:  '< > Grey check box', cursor=1",
     "SPEECH OUTPUT: 'Grey check box not checked.'",
     "SPEECH OUTPUT: 'Title of the Grey checkbox'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  'White'",
     "     VISIBLE:  'White', cursor=1",
     "SPEECH OUTPUT: 'White clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  '< > White check box'",
     "     VISIBLE:  '< > White check box', cursor=1",
     "SPEECH OUTPUT: 'White check box not checked.'",
     "SPEECH OUTPUT: 'ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'Black'",
     "     VISIBLE:  'Black', cursor=1",
     "SPEECH OUTPUT: 'Black clickable'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  '< > Black check box'",
     "     VISIBLE:  '< > Black check box', cursor=1",
     "SPEECH OUTPUT: 'Black check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Checkboxes with html labels:'",
     "     VISIBLE:  'Checkboxes with html labels:', cursor=1",
     "SPEECH OUTPUT: 'Checkboxes with html labels:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Grey'",
     "     VISIBLE:  'Grey', cursor=1",
     "SPEECH OUTPUT: 'Grey'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  '< > Title of the Grey checkbox check box'",
     "     VISIBLE:  '< > Title of the Grey checkbox c', cursor=1",
     "SPEECH OUTPUT: 'Title of the Grey checkbox check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'White'",
     "     VISIBLE:  'White', cursor=1",
     "SPEECH OUTPUT: 'White'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  '< > Title of the White checkbox check box'",
     "     VISIBLE:  '< > Title of the White checkbox ', cursor=1",
     "SPEECH OUTPUT: 'Title of the White checkbox check box not checked.'",
     "SPEECH OUTPUT: 'ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'Black'",
     "     VISIBLE:  'Black', cursor=1",
     "SPEECH OUTPUT: 'Black'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  '< > Title of the Black checkbox check box'",
     "     VISIBLE:  '< > Title of the Black checkbox ', cursor=1",
     "SPEECH OUTPUT: 'Title of the Black checkbox check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'Checkboxes without labels:'",
     "     VISIBLE:  'Checkboxes without labels:', cursor=1",
     "SPEECH OUTPUT: 'Checkboxes without labels:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  '.'",
     "     VISIBLE:  '.', cursor=1",
     "SPEECH OUTPUT: '.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'Baz'",
     "     VISIBLE:  'Baz', cursor=1",
     "SPEECH OUTPUT: 'Baz link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  ', and'",
     "     VISIBLE:  ', and', cursor=1",
     "SPEECH OUTPUT: ', and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  'Bar'",
     "     VISIBLE:  'Bar', cursor=1",
     "SPEECH OUTPUT: 'Bar link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  ','",
     "     VISIBLE:  ',', cursor=1",
     "SPEECH OUTPUT: ','"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo link.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
