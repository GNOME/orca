#!/usr/bin/python

"""Test to verify bug #469367 is still fixed.
   Orca StarOffice script not properly announcing (potential) indentation
   in OOo Writer.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_469367.params file that will
#    automatically load empty_document.odt. This uses the FreeSerif
#    font as the default which should be available on all test systems.
#
sequence.append(WaitForWindowActivate("empty_document(.odt|) - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Type Control-Home to move the text caret to the start of the document.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Enter two tabs, three spaces and the text "This is a test." followed by
#    Return.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("   This is a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Enter up arrow to position the text caret on the first line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Enter up arrow to position the text caret on the first line",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "empty_document", "		   This is a test. \$l") + "'",
     "     VISIBLE:  '		   This is a test. $l', cursor=1",
     "SPEECH OUTPUT: '		   This is a test.'"]))

######################################################################
# 5. Enter Insert-f to get text information.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert
sequence.append(utils.AssertPresentationAction(
    "Enter Insert-f to get text information",
    ["SPEECH OUTPUT: 'size 12'",
     "SPEECH OUTPUT: 'family name FreeSerif'"]))

######################################################################
# 6. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))

# We'll get a new window, but we'll wait for the "Save" button to get focus.
#
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
