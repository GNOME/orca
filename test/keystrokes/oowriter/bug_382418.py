#!/usr/bin/python

"""Test to verify bug #382418 is still fixed.
   Orca should announce when you enter/leave a table in OOo Writer documents.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"),None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, right arrow and Return.  (File->New->Text Document).
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Untitled 2 - " + utils.getOOoName("Writer"),None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Enter the following line and press Return:
#    Line 1
#
sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Enter Alt-a, right arrow and Return.  (Table->Insert->Table...).
#
sequence.append(KeyComboAction("<Alt>a"))
sequence.append(WaitForFocus("Insert", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Table...", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Name", acc_role=pyatspi.ROLE_TEXT))

######################################################################
# 5. Enter Return (Insert a table with the default parameters - 2x2).
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Type Control-Home to move the text caret to the start of the
#    document (and leave the table).
#
sequence.append(PauseAction(3000))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type Control-Home to move to start of document",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Line 1 \$l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Line 1 \$l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

######################################################################
# 7. Type a down arrow to enter the table.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to enter the table",

    ["BRAILLE LINE:  'table with 2 rows 2 columns'",
     "     VISIBLE:  'table with 2 rows 2 columns', cursor=0",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Table1-1 Table Paragraph'",
     "     VISIBLE:  'Paragraph', cursor=1",
     "SPEECH OUTPUT: 'table with 2 rows 2 columns'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'Cell A1'"]))

######################################################################
# 8. Enter Alt-f, Alt-c to close the Writer application.
#    A save dialog will appear.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 9. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# 10. Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
