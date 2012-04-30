#!/usr/bin/python

"""Test to verify bug #384893 is still fixed.
   Orca no longer reports bold or underline in OOo Writer when Insert F 
   is pressed.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_384893.params file that will
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
# 3. Enter the following (without the quotation marks) to create a
#    line with four words on it; the first one underlined and the
#    last one bold:
#      Control-u "This" Control-u " is a " Control-b "test" Control-b
#
sequence.append(KeyComboAction("<Control>u"))
sequence.append(TypeAction("This"))
sequence.append(KeyComboAction("<Control>u"))

sequence.append(TypeAction(" is a "))

sequence.append(KeyComboAction("<Control>b"))
sequence.append(TypeAction("test"))
sequence.append(KeyComboAction("<Control>b"))

######################################################################
# 4. Type Control-Home to position the text caret to the left of
#    the first character.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Type Control-Home to move to start of document",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "empty_document(.odt|)", "This is a test \$l") + "'",
     "     VISIBLE:  'This is a test $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test'"]))

######################################################################
# 5. Enter Insert-f to get text information on the underlined word.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Enter Insert-f to get text information on the underlined word",
    ["SPEECH OUTPUT: 'size 12'",
     "SPEECH OUTPUT: 'family name FreeSerif'",
     "SPEECH OUTPUT: 'underline single'",
     "SPEECH OUTPUT: 'paragraph style Default'"]))

######################################################################
# 6. Type Control right arrow three times to position the cursor at
#    the beginning of the bold word.
#
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyComboAction("<Control>Right"))

######################################################################
# 7. Enter Insert-f to get text information on the bold word. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Enter Insert-f to get text information on the bold word",
    ["SPEECH OUTPUT: 'size 12'",
     "SPEECH OUTPUT: 'family name FreeSerif'",
     "SPEECH OUTPUT: 'bold'",
     "SPEECH OUTPUT: 'paragraph style Default'"]))

######################################################################
# 8. Enter Alt-f, Alt-c to close the Writer application.
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
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
