#!/usr/bin/python

"""Test to verify bug #355733 is still fixed.
   Function "Say all" doesn't work correctly in Openoffice writer.
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
# 3. Enter four lines of text:
#    "Line 1"
#    "Line 2"
#    "Line 3"
#    "Line 4"
#
sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(TypeAction("Line 3"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(TypeAction("Line 4"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Enter Control-Home to return to the top of the document.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Return to top of document",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Line 1 \$l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view Line 1 \$l'",
     "     VISIBLE:  'Line 1 $l', cursor=1",
     "SPEECH OUTPUT: 'Line 1'"]))

######################################################################
# 5. Enter KP+ to perform a "say all" on the document.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add", 3000))
sequence.append(utils.AssertPresentationAction(
    "Say all on document",
    ["SPEECH OUTPUT: 'Line 1'",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'Line 3'",
     "SPEECH OUTPUT: 'Line 4'"]))

######################################################################
# 6. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 7. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# 8. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
