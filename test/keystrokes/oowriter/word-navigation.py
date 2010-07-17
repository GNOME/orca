#!/usr/bin/python

"""Test of Orca's presentation of Writer word navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# Start Writer
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# Create a new document
#
sequence.append(KeyComboAction("<Control>n"))
sequence.append(PauseAction(3000))

######################################################################
# Type a couple of short lines.
#
sequence.append(TypeAction("This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(TypeAction("So is this."))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# Control Home to return to the top of the document.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Top of document",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

######################################################################
# Control Right until in the next paragraph.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=9",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=11",
     "SPEECH OUTPUT: 'test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=16",
     "BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'So '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Next Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=4",
     "SPEECH OUTPUT: 'is '"]))

######################################################################
# Control Left back to the beginning.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "1. Previous Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "SPEECH OUTPUT: 'So '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=16",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=16",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=11",
     "SPEECH OUTPUT: 'test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=9",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=1",
     "SPEECH OUTPUT: 'This '"]))

######################################################################
# Control Right to select forward word by word
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Select Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=6",
     "SPEECH OUTPUT: 'This '",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Select Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=9",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Select Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=11",
     "SPEECH OUTPUT: 'a '",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Select Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Select Next Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Select Next Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=4",
     "SPEECH OUTPUT: 'So '",
     "SPEECH OUTPUT: 'selected'"]))

######################################################################
# Control Left to unselect word by word
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "1. Unselect Previous Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "SPEECH OUTPUT: 'So '",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=11",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=9",
     "SPEECH OUTPUT: 'a '",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=6",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Unselect Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=1",
     "SPEECH OUTPUT: 'This '",
     "SPEECH OUTPUT: 'unselected'"]))

######################################################################
# Control End to move to the end of the document.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Move to end of document",
    ["BUG? - Why are we saying 'unselected' here?",
     "BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "SPEECH OUTPUT: 'unselected'",
     "SPEECH OUTPUT: 'blank'"]))

######################################################################
# Control Left to select backward word by word
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "1. Select Previous Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=11",
     "BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=11",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Select Previous Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=7",
     "SPEECH OUTPUT: 'this'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Select Previous Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=4",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Select Previous Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "SPEECH OUTPUT: 'So '",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Select Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Select Previous Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=11",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'selected'"]))

######################################################################
# Control Right to unselect word by word
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Unselect Next Word",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=15",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Unselect Next Word",
    ["BUG? - Should we be saying 'unselected' here or not?",
     "BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Unselect Next Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=4",
     "SPEECH OUTPUT: 'So '",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Unselect Next Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=7",
     "SPEECH OUTPUT: 'is '",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Unselect Next Word",
    ["BRAILLE LINE:  'So is this. \$l'",
     "     VISIBLE:  'So is this. \$l', cursor=11",
     "SPEECH OUTPUT: 'this'",
     "SPEECH OUTPUT: 'unselected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Unselect Next Word",
    ["BUG? - Should we be saying 'dot unselected' instead?",
     "BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

######################################################################
# Close the new document
#
sequence.append(KeyComboAction("<Control>w"))
sequence.append(PauseAction(3000))

######################################################################
# Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# Wait before closing.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
