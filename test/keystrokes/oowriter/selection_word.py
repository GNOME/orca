#!/usr/bin/python

"""Test of Orca's presentation of Writer word navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("So is this."))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Select Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=6",
     "SPEECH OUTPUT: 'This '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Select Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=9",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Select Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'a '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Select Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Select Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "8. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=9",
     "SPEECH OUTPUT: 'a '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=6",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "11. Move to end of document",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  ' This is a test. $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(KeyComboAction("<Control><Shift>Left"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Select Previous Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=11",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Select Previous Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=7",
     "SPEECH OUTPUT: 'this'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "14. Select Previous Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=4",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "15. Select Previous Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=1",
     "SPEECH OUTPUT: 'So '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(KeyComboAction("<Control><Shift>Left"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "16. Select Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Select Previous Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "18. Unselect Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "19. Unselect Next Word",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Untitled 1 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(KeyComboAction("<Control><Shift>Right"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "20. Unselect Next Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=4",
     "SPEECH OUTPUT: 'So '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "21. Unselect Next Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=7",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "22. Unselect Next Word",
    ["BRAILLE LINE:  'So is this. $l'",
     "     VISIBLE:  'So is this. $l', cursor=11",
     "SPEECH OUTPUT: 'this'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
