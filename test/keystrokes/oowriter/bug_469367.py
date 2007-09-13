#!/usr/bin/python

"""Test to verify bug #469367 is still fixed.
   Orca StarOffice script not properly announcing (potential) indentation
   in OOo Writer.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, right arrow and Return.  (File->New->Text Document).
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", [0, 0, 0, 0, 0], pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", [0, 0, 0, 0, 0, 0], pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Untitled2 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Enter two tabs, three spaces and the text "This is a test." followed by
#    Return.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("   This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 1], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Enter up arrow to position the text caret on the first line.
#
sequence.append(KeyComboAction("Up"))
#sequence.append(WaitForFocus("", [-1, 0, 5, 0, 0, 0], pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Enter Insert-f to get text information.
#
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert

######################################################################
# 6. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", [-1, 0, 0, 0, 0], pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForWindowActivate("OpenOffice.org 2.3 ",None))
sequence.append(WaitForFocus("Save", [-1, 0], pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 7. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", [2, -1, 1], pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

sequence.start()
