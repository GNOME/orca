#!/usr/bin/python

"""Test presentation of caret navigation by word."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("So is this."))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=9",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  ' This is a test. $l', cursor=1",
     "BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=1",
     "SPEECH OUTPUT: 'blank' voice=system",
     "SPEECH OUTPUT: 'So '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Next Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=4",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Previous Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=1",
     "SPEECH OUTPUT: 'So '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "8. Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=9",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "11. Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Document view This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
