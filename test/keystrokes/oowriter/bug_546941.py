#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Test to verify bug #546941 is still fixed.
   When a list in OOo Writer gains focus, Orca does not display the
   selected list item in braille.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled[ ]*1 - " + utils.getOOoName("Writer"),None))
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
# 3. Type "This is a test."
#
sequence.append(TypeAction("This is a test."))

######################################################################
# 4. Select "test"
#
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("<Control><Shift>Left"))

######################################################################
# 5. Press Alt-o to bring up the Format menu.
#
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(WaitForFocus("Default Formatting", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 6. Press "h" to select "Character".
#
sequence.append(TypeAction("h"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_LIST))

######################################################################
# 7. Press Tab to move to move to Strikethrough.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_LIST))
sequence.append(utils.AssertPresentationAction(
    "Move to Strikethrough",
    ["BRAILLE LINE:  'soffice Application Character Dialog Character OptionPane TabList Font Effects Page Strikethrough (Without) Combo'",
     "     VISIBLE:  '(Without) Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Strikethrough (Without) combo box'"]))

######################################################################
# 8. Press Escape to exit the dialog.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 9. Enter Alt-f, Alt-c to close the Writer application.
#     A save dialog will appear.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 10. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# 11. Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled[ ]*1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
