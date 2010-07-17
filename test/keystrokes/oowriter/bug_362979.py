#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Test to verify bug #362979 is still fixed.
   In OOo, cannot read first character on line with bullets.
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
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Enter Alt-o to bring up the Format menu.
#
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(WaitForFocus("Default Formatting", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 4. Enter "b" to select "Bullets and Numbering..."
#
sequence.append(TypeAction("b"))
sequence.append(WaitForFocus("Selection", acc_role=pyatspi.ROLE_LIST))

######################################################################
# 5. Enter Tab and Return to select small dot bullets.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Enter the following two lines, each followed by a Return to
#    create two bulleted lines:
#      Line 1
#      Line 2
#
sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 7. Enter a Return to exit bulleting.
#
sequence.append(KeyComboAction("Return"))

######################################################################
# 8. Enter Control-Home to position the text caret to the left of
#    the first character on the first line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Move cursor to start of document",
    ["BRAILLE LINE:  'soffice Application Untitled 2 - " + utils.getOOoName("Writer") + " Frame Untitled 2 - " + utils.getOOoName("Writer") + " RootPane ScrollPane Document view •Line 1 \$l'",
     "     VISIBLE:  '•Line 1 \$l', cursor=2",
     "SPEECH OUTPUT: '•Line 1'"]))

######################################################################
# 9. Type a down arrow to go to the second bulleted line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Move to second bulleted line",
    ["BRAILLE LINE:  '•Line 2 \$l'",
     "     VISIBLE:  '•Line 2 \$l', cursor=2",
     "BRAILLE LINE:  '•Line 2 \$l'",
     "     VISIBLE:  '•Line 2 \$l', cursor=2",
     "SPEECH OUTPUT: '•Line 2'"]))

######################################################################
# 10. Enter Alt-f, Alt-c to close the Writer application.
#     A save dialog will appear.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 11. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# 12. Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
