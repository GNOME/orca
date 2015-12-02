#!/usr/bin/python

"""Test of line navigation on a page with multi-line cells and sections."""

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
    ["BRAILLE LINE:  'Table test'",
     "     VISIBLE:  'Table test', cursor=1",
     "SPEECH OUTPUT: 'Table test'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'foo bar'",
     "     VISIBLE:  'foo bar', cursor=1",
     "SPEECH OUTPUT: 'foo.'",
     "SPEECH OUTPUT: 'bar.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Hello h3'",
     "     VISIBLE:  'Hello h3', cursor=1",
     "SPEECH OUTPUT: 'Hello heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  '• This is a test that is not very interesting.'",
     "     VISIBLE:  '• This is a test that is not ver', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'This is a test'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'that is not very interesting.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  '• But it looks like a real-world example.'",
     "     VISIBLE:  '• But it looks like a real-world', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'But it looks like'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'a real-world example.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  '• And that's why this silly test is here.'",
     "     VISIBLE:  '• And that's why this silly test', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'And that's'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'why this silly test is here.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'So it's far more interesting than it looks.'",
     "     VISIBLE:  'So it's far more interesting tha', cursor=1",
     "SPEECH OUTPUT: 'So it's'",
     "SPEECH OUTPUT: 'far more interesting'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'than it looks.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'World h3'",
     "     VISIBLE:  'World h3', cursor=1",
     "SPEECH OUTPUT: 'World heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  '• The thing is we can't copy content.'",
     "     VISIBLE:  '• The thing is we can't copy con', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'The thing is'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'we can't copy content.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  '• So we must create silly tests.'",
     "     VISIBLE:  '• So we must create silly tests.', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'So we must'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'create silly tests.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  '• Oh well.'",
     "     VISIBLE:  '• Oh well.', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'Oh'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'well.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'At least it's over.'",
     "     VISIBLE:  'At least it's over.', cursor=1",
     "SPEECH OUTPUT: 'At least it's'",
     "SPEECH OUTPUT: 'over'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: '.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  '• Oh well.'",
     "     VISIBLE:  '• Oh well.', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'Oh'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'well.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  '• So we must create silly tests.'",
     "     VISIBLE:  '• So we must create silly tests.', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'So we must'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'create silly tests.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  '• The thing is we can't copy content.'",
     "     VISIBLE:  '• The thing is we can't copy con', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'The thing is'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'we can't copy content.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  'World h3'",
     "     VISIBLE:  'World h3', cursor=1",
     "SPEECH OUTPUT: 'World heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  'So it's far more interesting than it looks.'",
     "     VISIBLE:  'So it's far more interesting tha', cursor=1",
     "SPEECH OUTPUT: 'So it's'",
     "SPEECH OUTPUT: 'far more interesting'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'than it looks.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Up",
    ["BRAILLE LINE:  '• And that's why this silly test is here.'",
     "     VISIBLE:  '• And that's why this silly test', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'And that's'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'why this silly test is here.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Up",
    ["BRAILLE LINE:  '• But it looks like a real-world example.'",
     "     VISIBLE:  '• But it looks like a real-world', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'But it looks like'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'a real-world example.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Up",
    ["BRAILLE LINE:  '• This is a test that is not very interesting.'",
     "     VISIBLE:  '• This is a test that is not ver', cursor=1",
     "SPEECH OUTPUT: '•.'",
     "SPEECH OUTPUT: 'This is a test'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'that is not very interesting.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  'Hello h3'",
     "     VISIBLE:  'Hello h3', cursor=1",
     "SPEECH OUTPUT: 'Hello heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Up",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Up",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Up",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Up",
    ["BRAILLE LINE:  'foo bar'",
     "     VISIBLE:  'foo bar', cursor=1",
     "SPEECH OUTPUT: 'foo.'",
     "SPEECH OUTPUT: 'bar.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  'Table test'",
     "     VISIBLE:  'Table test', cursor=1",
     "SPEECH OUTPUT: 'Table test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
