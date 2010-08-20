#!/usr/bin/python

"""Test to verify we announce the (likely accidental) addition and
   subsequent removal of a row at the end of a table."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"),None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# Create a new document.
#
sequence.append(KeyComboAction("<Ctrl>n"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(PauseAction(3000))

######################################################################
# Ctrl+F12, Return to create a new table
#
sequence.append(KeyComboAction("<Ctrl>F12"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(PauseAction(3000))

######################################################################
# Tab to move through the cells and, eventually create a new row.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "1. Tab",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Table1-1 Table Paragraph'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell B1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Table1-1 Table Paragraph'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell A2"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Table1-1 Table Paragraph'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'End of table blank'",
     "SPEECH OUTPUT: 'Cell B2"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  'Row inserted at the end of the table.'",
     "     VISIBLE:  'Row inserted at the end of the t', cursor=0",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Table1-1 Table Paragraph'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'Row inserted at the end of the table.'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell A3"]))

######################################################################
# Ctrl+Z to undo the creation of the new row.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Ctrl>z"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Z",
    ["BRAILLE LINE:  'Last row deleted.'",
     "     VISIBLE:  'Last row deleted.', cursor=0",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Table1-1 Table Paragraph'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'Last row deleted.'",
     "SPEECH OUTPUT: 'End of table blank'",
     "SPEECH OUTPUT: 'Cell B2"]))

######################################################################
#  Alt-f, Alt-c to close the Writer application.
#  A save dialog will appear.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
#  Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
